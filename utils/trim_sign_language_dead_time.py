import json
import os
import numpy as np

def detect_motion_and_trim(output_data, motion_threshold=0.2, min_active_frames=5):
    """Trim dead time from motion data based on motion threshold."""
    frame_motion = []
    
    # Calculate motion between consecutive frames
    for i in range(1, len(output_data)):
        prev_frame = output_data[i - 1]['pose']
        curr_frame = output_data[i]['pose']
        
        # Calculate Euclidean distance for corresponding landmarks
        motion = np.sqrt(sum(
            (curr['x'] - prev['x']) ** 2 + 
            (curr['y'] - prev['y']) ** 2 + 
            (curr['z'] - prev['z']) ** 2
            for curr, prev in zip(curr_frame, prev_frame)
        )) if prev_frame and curr_frame else 0  # Handle empty pose data
        
        frame_motion.append(motion)
    
    # Detect the start frame with significant motion
    active_frames = 0
    start_frame = None
    
    for i, motion in enumerate(frame_motion):
        if motion > motion_threshold:
            active_frames += 1
            if active_frames >= min_active_frames:
                start_frame = i - min_active_frames + 2  # +2 to adjust for frame index
                break
        else:
            active_frames = 0
    
    # Trim the data from the start_frame onward
    trimmed_data = output_data[start_frame:] if start_frame is not None else []
    
    return trimmed_data
