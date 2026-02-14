from enum import Enum

class ZoneType(str, Enum):
    """Allowed areas"""
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class NodeCategory(str, Enum):
    """Node role on simulation"""
    START = "start"
    END = "end"
    INTERMEDIATE = "intermediate"
