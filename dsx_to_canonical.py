import argparse
import hashlib
import json
import os
import re
from datetime import datetime


def build_canonical_from_text(dsx_text: str, *, file_name: str = "uploaded.dsx") -> dict:
    """Build canonical DSX representation from raw DSX text.

    This is the DB-ready entrypoint: callers can ingest uploads directly without
    writing the DSX to disk.
    """

    lines = dsx_text.splitlines(True)  # keep newlines to match file.readlines()

    header = parse_header(lines)
    export_ts = _parse_header_timestamp(header)
    root = parse_job_root(lines) or {}
    dsjob_modified = parse_dsjob_modified(lines)
    if not root.get('date_modified') and dsjob_modified:
        root['date_modified'] = dsjob_modified
    container = parse_container_view(lines)
    stages_by_ident = parse_stages_minimal(lines)
    pins = parse_pins(lines)

    # Build a mapping: targetStageId -> list of input pin identifiers
    # Pin Partner looks like: "V0S152|V0S152P1" meaning (partnerStageId|partnerPinId)
    # For an input pin record belonging to stage V0S152P1, the record Identifier is V0S152P1.
    # We'll use Partner to determine which stage this pin connects to.
    target_stage_to_input_pins = {}
    for p in pins:
        ole = p.get('OLEType', '')
        if 'Input' not in ole:
            continue

        this_pin_id = p.get('Identifier')
        partner = p.get('Partner', '')
        if not this_pin_id or not partner:
            continue

        # Partner is the upstream side; the *owner stage* of this pin comes from the pin id prefix.
        owner_stage_match = re.match(r'([A-Za-z0-9]+)P\d+$', this_pin_id)
        if not owner_stage_match:
            continue
        owner_stage_id = owner_stage_match.group(1)

        target_stage_to_input_pins.setdefault(owner_stage_id, []).append(this_pin_id)

    dsx_file_id = _stable_id("dsx", file_name)
    file_checksum = hashlib.sha256(dsx_text.encode("utf-8", errors="replace")).hexdigest()

    # Stages from container view (authoritative list)
    stage_ids = [s.strip() for s in (container.get('StageList', '')).split('|')]
    stage_names = [s.strip() for s in (container.get('StageNames', '')).split('|')]
    stage_typeids = [s.strip() for s in (container.get('StageTypeIDs', '')).split('|')]

    # These arrays can contain leading blanks; align by index.
    stage_entries = []
    id_to_stage_id = {}
    for idx in range(max(len(stage_ids), len(stage_names), len(stage_typeids))):
        sid = stage_ids[idx] if idx < len(stage_ids) else ""
        sname = stage_names[idx] if idx < len(stage_names) else ""
        stype = stage_typeids[idx] if idx < len(stage_typeids) else ""

        if not sid and not sname:
            continue

        # The container view sometimes includes non-stage identifiers in StageList
        # where the corresponding StageNames entry is blank (e.g., "V0A5", "V36A0").
        # Treat these as non-stages and skip them.
        if sid and not sname:
            continue

        record = stages_by_ident.get(sid, {})
        ole_type = record.get('OLEType', '')
        # Determine category heuristically
        cat = "Unknown"
        if ole_type == 'CTransformerStage' or 'Transformer' in stype:
            cat = "Transform"
        elif 'SequentialFile' in stype or 'File' in stype:
            cat = "Source"
        elif 'Connector' in stype:
            # Could be source or target; DSX often has Properties specifying target/source but that's in subrecords.
            cat = "Unknown"

        # Include dsx_file_id so stage IDs never collide across different uploads/files.
        canonical_stage_id = _stable_id("stage", dsx_file_id, root.get('identifier', ''), sid, sname, stype, ole_type)
        id_to_stage_id[sid] = canonical_stage_id

        # Minimal properties bag: include a few record fields that are stable
        props = {}
        for k in ('StageType', 'OLEType', 'InputPins', 'OutputPins', 'AllowColumnMapping'):
            if k in record:
                props[k] = record[k]

        stage_entries.append(
            {
                "stage_id": canonical_stage_id,
                "stage_name": sname or record.get('Name', sid),
                "identifier": sid,
                "stage_type": stype or record.get('StageType', ''),
                "ole_type": ole_type,
                "category": cat,
                "properties": _kv_bag(props),
                "input_links": [],
                "output_links": [],
                "columns": [],
                "transform": None,
                "view": None,
            }
        )

    # Links from container view
    link_names = [s.strip() for s in (container.get('LinkNames', '')).split('|')]
    link_source_pins = [s.strip() for s in (container.get('LinkSourcePinIDs', '')).split('|')]
    target_stage_ids = [s.strip() for s in (container.get('TargetStageIDs', '')).split('|')]

    links = []
    for link_name, src_pin, tgt_sid in zip(link_names, link_source_pins, target_stage_ids):
        if not link_name or not src_pin or not tgt_sid:
            continue

        # Some DSX exports (notably large jobs) pack multiple link names/pins/stages
        # into a single index separated by commas. Split them into individual links.
        link_name_parts = [p.strip() for p in link_name.split(',') if p.strip()]
        src_pin_parts = [p.strip() for p in src_pin.split(',') if p.strip()]
        tgt_sid_parts = [p.strip() for p in tgt_sid.split(',') if p.strip()]

        # If only one of the fields is comma-separated, fall back to treating it as a single link.
        n = max(len(link_name_parts), len(src_pin_parts), len(tgt_sid_parts))
        if n == 1:
            triplets = [(link_name, src_pin, tgt_sid)]
        else:
            # Align by index. If lengths mismatch, truncate to the shortest to avoid wrong wiring.
            n = min(len(link_name_parts), len(src_pin_parts), len(tgt_sid_parts))
            triplets = list(zip(link_name_parts[:n], src_pin_parts[:n], tgt_sid_parts[:n]))

        for ln, sp, ts in triplets:
            src_match = re.match(r'([A-Za-z0-9]+)P\d+', sp)
            src_sid = src_match.group(1) if src_match else sp

            source_stage_id = id_to_stage_id.get(src_sid) or _stable_id("stage", dsx_file_id, src_sid)
            target_stage_id = id_to_stage_id.get(ts) or _stable_id("stage", dsx_file_id, ts)

            # Include dsx_file_id so link IDs never collide across different uploads/files.
            link_id = _stable_id("link", dsx_file_id, root.get('identifier', ''), ln, src_sid, ts)

            # Best-effort target pin id: if target stage has exactly one input pin, use it.
            target_pin_id = None
            candidate_pins = target_stage_to_input_pins.get(ts, [])
            if len(candidate_pins) == 1:
                target_pin_id = candidate_pins[0]

            links.append(
                {
                    "link_id": link_id,
                    "link_name": ln,
                    "source_stage_id": source_stage_id,
                    "target_stage_id": target_stage_id,
                    "source_pin_id": sp,
                    "target_pin_id": target_pin_id,
                    "row_count_hint": None,
                    "description": None,
                    "schema": None,
                }
            )

    # backfill stage input/output link names
    stage_by_id = {s["stage_id"]: s for s in stage_entries}
    for l in links:
        stage_by_id.get(l["source_stage_id"], {}).setdefault("output_links", []).append(l["link_name"])
        stage_by_id.get(l["target_stage_id"], {}).setdefault("input_links", []).append(l["link_name"])

    # Parameters normalization
    params = []
    for p in root.get('parameters', []) or []:
        # Map DSX ParamType (0=string,1=password,4=apt_config) roughly
        ptype = p.get('ParamType')
        data_type = "string"
        if ptype == '1':
            data_type = "password"
        elif ptype == '4':
            data_type = "apt_config"

        params.append(
            {
                "name": p.get('Name'),
                "data_type": data_type,
                "default_value": p.get('Default'),
                "prompt": p.get('Prompt'),
                "required": False,
                "raw": _kv_bag({k: v for k, v in p.items() if k not in {'Name', 'Default', 'Prompt'}}),
            }
        )

    job_identifier = root.get('identifier') or os.path.splitext(file_name)[0]
    # Include dsx_file_id so job IDs never collide across different uploads/files.
    job_id = _stable_id("job", dsx_file_id, job_identifier)

    doc = {
        "canonical_version": "1.0",
        "dsx_file_id": dsx_file_id,
        "file_name": file_name,
        "file_checksum": file_checksum,
        "project_name": None,
        "exporting_tool": header.get('ExportingTool'),
        "tool_version": header.get('ToolVersion'),
        "server_version": header.get('ServerVersion'),
        "export_timestamp": export_ts,
        "raw": {
            "header_text": None,
            "dsjob_text": None,
        },
        "jobs": [
            {
                "job_id": job_id,
                "job_name": root.get('name') or job_identifier,
                "identifier": job_identifier,
                "description": root.get('description'),
                "developer": None,
                "job_version": root.get('job_version'),
                "date_modified": root.get('date_modified'),
                "category": root.get('category'),
                "parameters": params,
                "stages": stage_entries,
                "links": links,
                "routines": None,
                "annotations": None,
                "raw_refs": {
                    "root_record_id": "ROOT",
                    "container_view_id": "Job",
                },
            }
        ],
    }

    return doc


def _stable_id(*parts: str) -> str:
    joined = "|".join(p if p is not None else "" for p in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def _kv_bag(d: dict) -> dict:
    items = [{"key": str(k), "value": "" if v is None else str(v)} for k, v in d.items()]
    items.sort(key=lambda x: x["key"])
    return {"items": items}


def _find_block(lines, start_marker, end_marker, start_idx=0):
    start = end = None
    for i, line in enumerate(lines[start_idx:], start=start_idx):
        s = line.strip()
        if start is None and s.startswith(start_marker):
            start = i
        elif start is not None and s.startswith(end_marker):
            end = i
            break
    return start, end


def parse_header(lines):
    start, end = _find_block(lines, "BEGIN HEADER", "END HEADER")
    if start is None or end is None:
        return {}
    text = "".join(lines[start + 1 : end])
    # Key "Value" pairs
    return dict(re.findall(r"\s*(\w+)\s+\"([^\"]*)\"", text))


def _parse_header_timestamp(header: dict):
    """Return ISO timestamp from DSX header Date/Time when available."""
    d = header.get("Date")
    t = header.get("Time")
    if not d or not t:
        return None
    # DSX header time often uses dots: 17.42.13
    t = t.replace(".", ":")
    try:
        return datetime.fromisoformat(f"{d}T{t}").isoformat()
    except ValueError:
        return None


def parse_dsjob_modified(lines):
    """Parse DSJOB-level DateModified/TimeModified which appear near the top of BEGIN DSJOB."""
    job_start, job_end = _find_block(lines, "BEGIN DSJOB", "END DSJOB")
    if job_start is None or job_end is None:
        return None

    date_modified = None
    time_modified = None
    for i in range(job_start, min(job_start + 80, job_end)):
        s = lines[i].strip()
        m = re.match(r'DateModified\s+"([^\"]+)"', s)
        if m:
            date_modified = m.group(1)
        m = re.match(r'TimeModified\s+"([^\"]+)"', s)
        if m:
            time_modified = m.group(1)

    if date_modified and time_modified:
        t = time_modified.replace(".", ":")
        try:
            return datetime.fromisoformat(f"{date_modified}T{t}").isoformat()
        except ValueError:
            return None
    return None


def parse_job_root(lines):
    job_start, job_end = _find_block(lines, "BEGIN DSJOB", "END DSJOB")
    if job_start is None or job_end is None:
        return None

    # Find ROOT DSRECORD
    root_start = root_end = None
    inside = False
    for i in range(job_start, job_end):
        if lines[i].strip().startswith("BEGIN DSRECORD"):
            inside = True
            # DSX often has Identifier "ROOT" within a couple lines
            probe = "".join(lines[i : min(i + 8, job_end)])
            if re.search(r'Identifier\s+"ROOT"', probe):
                root_start = i
        elif inside and root_start is not None and lines[i].strip().startswith("END DSRECORD"):
            root_end = i
            break

    if root_start is None or root_end is None:
        return None

    name = None
    description = None
    identifier = None
    date_modified = None
    time_modified = None
    job_version = None
    category = None

    parameters = []

    in_full_desc = False
    full_desc_lines = []
    in_params_section = False

    i = root_start
    while i < root_end:
        line = lines[i].strip()

        m = re.match(r'Identifier\s+"([^\"]+)"', line)
        if m and identifier is None:
            identifier = m.group(1)

        m = re.match(r'Name\s+"([^\"]+)"', line)
        if m and name is None:
            name = m.group(1)

        m = re.match(r'DateModified\s+"([^\"]+)"', line)
        if m and date_modified is None:
            date_modified = m.group(1)

        m = re.match(r'TimeModified\s+"([^\"]+)"', line)
        if m and time_modified is None:
            time_modified = m.group(1)

        m = re.match(r'JobVersion\s+"([^\"]+)"', line)
        if m and job_version is None:
            job_version = m.group(1)

        m = re.match(r'Category\s+"([^\"]+)"', line)
        if m and category is None:
            category = m.group(1)

        if line.startswith("Description ") and description is None:
            # fallback short description
            parts = line.split(" ", 1)
            if len(parts) == 2:
                description = parts[1].strip('"')

        if line.startswith("FullDescription"):
            if "=+=+=+=" in line:
                in_full_desc = True
                full_desc_lines = []
            else:
                parts = line.split(" ", 1)
                if len(parts) == 2:
                    description = parts[1].strip('"')

        elif in_full_desc:
            if "=+=+=+=" in line:
                in_full_desc = False
                description = "\n".join(full_desc_lines).strip()
            else:
                full_desc_lines.append(line)

        if line.startswith('Parameters "CParameters"'):
            in_params_section = True
        elif in_params_section and line.startswith('MetaBag'):
            in_params_section = False
        elif in_params_section and line.startswith('BEGIN DSSUBRECORD'):
            param = {}
            i += 1
            while i < root_end and not lines[i].strip().startswith('END DSSUBRECORD'):
                mm = re.match(r'(\w+)\s+"([^\"]*)"', lines[i].strip())
                if mm:
                    k, v = mm.groups()
                    param[k] = v
                i += 1
            if param.get('Name'):
                parameters.append(param)

        i += 1

    # Build ISO datetime if possible
    modified_ts = None
    if date_modified and time_modified:
        # DSX time looks like 15.41.15
        t = time_modified.replace(".", ":")
        # DSX date can be yyyy-mm-dd OR yyyy-mm-dd
        try:
            modified_ts = datetime.fromisoformat(f"{date_modified}T{t}").isoformat()
        except ValueError:
            modified_ts = None

    return {
        "identifier": identifier,
        "name": name,
        "description": description,
        "job_version": job_version,
        "category": category,
        "date_modified": modified_ts,
        "parameters": parameters,
    }


def parse_container_view(lines):
    # Extract key arrays from the main container view: OLEType "CContainerView" and Name "Job"
    content = "".join(lines)
    for m in re.finditer(r'BEGIN DSRECORD\s*(.*?)END DSRECORD', content, re.DOTALL):
        body = m.group(1)
        if re.search(r'OLEType\s+"CContainerView"', body) and re.search(r'Name\s+"Job"', body):
            def _get(field):
                mm = re.search(rf'{re.escape(field)}\s+"([^\"]*)"', body)
                return mm.group(1) if mm else ""

            return {
                "StageList": _get("StageList"),
                "StageNames": _get("StageNames"),
                "StageTypeIDs": _get("StageTypeIDs"),
                "StageTypes": _get("StageTypes"),
                "LinkNames": _get("LinkNames"),
                "TargetStageIDs": _get("TargetStageIDs"),
                "LinkSourcePinIDs": _get("LinkSourcePinIDs"),
                "StageXPos": _get("StageXPos"),
                "StageYPos": _get("StageYPos"),
                "StageXSize": _get("StageXSize"),
                "StageYSize": _get("StageYSize"),
            }
    return {}


def parse_stages_minimal(lines):
    # Minimal stage records parser: extract Identifier, Name, OLEType, StageType.
    stages = {}
    in_record = False
    in_sub = False
    record = {}

    for line in lines:
        s = line.strip()
        if s.startswith('BEGIN DSRECORD'):
            in_record = True
            in_sub = False
            record = {}
            continue
        if s.startswith('END DSRECORD') and in_record:
            ole = record.get('OLEType', '')
            if ole.endswith('Stage') or ole == 'CCustomStage':
                ident = record.get('Identifier') or record.get('Name') or _stable_id("stage", str(record))
                stages[ident] = record
            in_record = False
            continue

        if not in_record:
            continue

        if s.startswith('BEGIN DSSUBRECORD'):
            in_sub = True
            continue
        if s.startswith('END DSSUBRECORD'):
            in_sub = False
            continue
        if in_sub:
            continue

        mm = re.match(r'(\w+)\s+"([^\"]*)"', s)
        if mm:
            k, v = mm.groups()
            record[k] = v

    return stages


def parse_pins(lines):
    """Parse pin records so we can resolve link target pin IDs via Partner mapping."""
    pins = []
    in_record = False
    in_sub = False
    record = {}

    for line in lines:
        s = line.strip()
        if s.startswith('BEGIN DSRECORD'):
            in_record = True
            in_sub = False
            record = {}
            continue
        if s.startswith('END DSRECORD') and in_record:
            ole = record.get('OLEType', '')
            if ole in {'CTrxInput', 'CTrxOutput', 'CCustomInput', 'CCustomOutput'}:
                pins.append(record)
            in_record = False
            continue

        if not in_record:
            continue

        if s.startswith('BEGIN DSSUBRECORD'):
            in_sub = True
            continue
        if s.startswith('END DSSUBRECORD'):
            in_sub = False
            continue
        if in_sub:
            continue

        mm = re.match(r'(\w+)\s+"([^\"]*)"', s)
        if mm:
            k, v = mm.groups()
            record[k] = v

    return pins


def build_canonical(dsx_path: str) -> dict:
    file_name = os.path.basename(dsx_path)
    with open(dsx_path, 'r', encoding='utf-8', errors='replace') as f:
        dsx_text = f.read()
    return build_canonical_from_text(dsx_text, file_name=file_name)


def main():
    ap = argparse.ArgumentParser(description="Convert a DSX file to canonical JSON model")
    ap.add_argument("dsx_path", help="Path to .dsx file")
    ap.add_argument("-o", "--output", help="Output JSON file path")
    args = ap.parse_args()

    out = build_canonical(args.dsx_path)

    if args.output:
        out_path = args.output
    else:
        base = os.path.splitext(os.path.basename(args.dsx_path))[0]
        out_path = f"{base}.canonical.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    print(f"Wrote canonical JSON: {out_path}")


if __name__ == "__main__":
    main()
