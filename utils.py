"""
Shared utility functions for DSX Documentation Assistant.

This module consolidates commonly-used helper functions that were previously
duplicated across multiple files.
"""

import hashlib
import re
import sqlite3
from datetime import datetime, timezone
from typing import List


def stable_id(*parts: str) -> str:
    """
    Create a stable, deterministic ID from string parts.
    
    Args:
        *parts: Variable number of string components
        
    Returns:
        SHA256 hex digest of joined parts
        
    Example:
        >>> stable_id("job", "MyJob", "v1")
        'a1b2c3d4...'
    """
    combined = "|".join(str(p) for p in parts)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def sha256_hex(s: str) -> str:
    """
    Compute SHA256 hash of a string.
    
    Args:
        s: Input string
        
    Returns:
        Hex digest of SHA256 hash
    """
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def safe_filename(name: str, max_len: int = 200) -> str:
    """
    Convert a string into a safe filesystem filename.
    
    Removes/replaces characters that are problematic on Windows/Unix filesystems.
    
    Args:
        name: Original filename/string
        max_len: Maximum length (default: 200)
        
    Returns:
        Sanitized filename safe for all platforms
        
    Example:
        >>> safe_filename("My Job: Version 2.0")
        'My_Job_Version_2_0'
    """
    # Replace common problematic characters
    s = name.replace("/", "_").replace("\\", "_")
    s = s.replace(":", "_").replace("*", "_")
    s = s.replace("?", "_").replace('"', "_")
    s = s.replace("<", "_").replace(">", "_")
    s = s.replace("|", "_")
    
    # Collapse multiple underscores/spaces
    s = re.sub(r"[_\s]+", "_", s)
    
    # Remove leading/trailing underscores
    s = s.strip("_")
    
    # Truncate to max length
    return s[:max_len] if len(s) > max_len else s


def utcnow_iso() -> str:
    """
    Get current UTC timestamp in ISO format.
    
    Returns:
        ISO 8601 formatted timestamp string
        
    Example:
        >>> utcnow_iso()
        '2026-03-09T14:30:00Z'
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def connect_db(db_path: str, check_same_thread: bool = True) -> sqlite3.Connection:
    """
    Create a database connection with standard settings.
    
    Args:
        db_path: Path to SQLite database file
        check_same_thread: SQLite thread safety check (default: True)
        
    Returns:
        SQLite connection object
    """
    conn = sqlite3.connect(db_path, check_same_thread=check_same_thread)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def fetchall(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> List[tuple]:
    """
    Execute a SELECT query and return all results.
    
    Args:
        conn: SQLite connection
        sql: SQL query string
        params: Query parameters (default: empty tuple)
        
    Returns:
        List of result tuples
    """
    cursor = conn.execute(sql, params)
    return cursor.fetchall()


def execute_sql(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> sqlite3.Cursor:
    """
    Execute a SQL statement and return the cursor.
    
    Args:
        conn: SQLite connection
        sql: SQL statement
        params: Statement parameters (default: empty tuple)
        
    Returns:
        SQLite cursor
    """
    return conn.execute(sql, params)
