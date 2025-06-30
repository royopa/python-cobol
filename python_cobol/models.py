"""
Data models for COBOL Copybook parsing.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PicInfo:
    """Represents PIC clause information."""
    
    type: str
    length: int
    precision: int
    
    def __str__(self) -> str:
        return (
            f"PicInfo(type={self.type}, "
            f"length={self.length}, precision={self.precision})"
        )


@dataclass
class CobolField:
    """Represents a COBOL field definition."""
    
    level: int
    name: str
    pic: Optional[str] = None
    pic_info: Optional[PicInfo] = None
    occurs: Optional[int] = None
    indexed_by: Optional[str] = None
    redefines: Optional[str] = None
    
    def __str__(self) -> str:
        parts = [f"{self.level:02d} {self.name}"]
        
        if self.redefines:
            parts.append(f"REDEFINES {self.redefines}")
        
        if self.occurs:
            parts.append(f"OCCURS {self.occurs} TIMES")
            
        if self.indexed_by:
            parts.append(f"INDEXED BY {self.indexed_by}")
            
        if self.pic:
            parts.append(f"PIC {self.pic}")
            
        return " ".join(parts) + "."
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'level': self.level,
            'name': self.name,
            'pic': self.pic,
            'pic_info': self.pic_info.__dict__ if self.pic_info else None,
            'occurs': self.occurs,
            'indexed_by': self.indexed_by,
            'redefines': self.redefines,
        } 