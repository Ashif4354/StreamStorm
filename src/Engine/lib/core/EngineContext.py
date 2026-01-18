from dataclasses import dataclass

@dataclass
class EngineContext:
    
    # Class-level state (shared across all instances/imports)
    _busy: bool = False
    _busy_reason: str = ""
    
    @classmethod
    def is_busy(cls) -> bool:
        """Check if the engine is currently busy."""
        return cls._busy
    
    @classmethod
    def get_busy_reason(cls) -> str:
        """Get the reason why the engine is busy."""
        return cls._busy_reason
    
    @classmethod
    def set_busy(cls, reason: str) -> None:
        """Set the engine as busy with a reason."""
        cls._busy = True
        cls._busy_reason = reason
    
    @classmethod
    def reset(cls) -> None:
        """Reset the engine to not busy state."""
        cls._busy = False
        cls._busy_reason = ""


__all__: list[str] = ["EngineContext"]
