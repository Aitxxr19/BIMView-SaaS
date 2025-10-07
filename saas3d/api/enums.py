import enum

class JobStatus(str, enum.Enum):
    queued = 'queued'
    processing = 'processing'
    completed = 'completed'
    failed = 'failed'
