import numpy as np

def add(data1, data2, width):
    """Add two bytes objects containing audio samples."""
    if width == 1:
        arr1 = np.frombuffer(data1, dtype=np.int8)
        arr2 = np.frombuffer(data2, dtype=np.int8)
    elif width == 2:
        arr1 = np.frombuffer(data1, dtype=np.int16)
        arr2 = np.frombuffer(data2, dtype=np.int16)
    elif width == 4:
        arr1 = np.frombuffer(data1, dtype=np.int32)
        arr2 = np.frombuffer(data2, dtype=np.int32)
    else:
        raise ValueError(f"Unsupported width: {width}")
    result = arr1 + arr2
    result = np.clip(result, -2**(width*8-1), 2**(width*8-1)-1)
    return result.tobytes()

def bias(data, bias, width):
    """Add a bias to each sample."""
    if width == 1:
        arr = np.frombuffer(data, dtype=np.int8)
    elif width == 2:
        arr = np.frombuffer(data, dtype=np.int16)
    elif width == 4:
        arr = np.frombuffer(data, dtype=np.int32)
    else:
        raise ValueError(f"Unsupported width: {width}")
    result = arr + bias
    result = np.clip(result, -2**(width*8-1), 2**(width*8-1)-1)
    return result.tobytes()

def findmax(data, width):
    """Find the maximum value in the audio samples."""
    if width == 1:
        arr = np.frombuffer(data, dtype=np.int8)
    elif width == 2:
        arr = np.frombuffer(data, dtype=np.int16)
    elif width == 4:
        arr = np.frombuffer(data, dtype=np.int32)
    else:
        raise ValueError(f"Unsupported width: {width}")
    if len(arr) == 0:
        return 0
    return int(np.max(np.abs(arr)))

def lin2lin(data, from_width, to_width):
    """Convert linear samples from one width to another."""
    if from_width == to_width:
        return data
    if from_width == 1:
        arr = np.frombuffer(data, dtype=np.int8)
    elif from_width == 2:
        arr = np.frombuffer(data, dtype=np.int16)
    elif from_width == 4:
        arr = np.frombuffer(data, dtype=np.int32)
    else:
        raise ValueError(f"Unsupported from_width: {from_width}")
    if to_width == 1:
        arr = np.clip(arr, -128, 127).astype(np.int8)
    elif to_width == 2:
        arr = np.clip(arr, -32768, 32767).astype(np.int16)
    elif to_width == 4:
        arr = np.clip(arr, -2147483648, 2147483647).astype(np.int32)
    else:
        raise ValueError(f"Unsupported to_width: {to_width}")
    return arr.tobytes()

def ratecv(data, width, nchannels, inrate, outrate, state):
    """Convert the sample rate of audio data."""
    # Simple implementation for compatibility
    if width == 1:
        arr = np.frombuffer(data, dtype=np.int8)
    elif width == 2:
        arr = np.frombuffer(data, dtype=np.int16)
    elif width == 4:
        arr = np.frombuffer(data, dtype=np.int32)
    else:
        raise ValueError(f"Unsupported width: {width}")
    # For simplicity, just return the original data
    return data, state
