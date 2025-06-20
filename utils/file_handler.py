import os
import glob
import time
from pathlib import Path

def get_latest_file(directory):
    """Get the most recently created/modified file in the directory."""
    files = glob.glob(os.path.join(directory, '*'))
    if not files:
        return None
    return max(files, key=os.path.getctime)

def is_error_file(file_path):
    """Check if the file is an error file based on Hebrew error message."""
    if not file_path or not os.path.exists(file_path):
        return False
        
    error_messages = ['נכשלה', 'שגיאה', 'error']
    filename = os.path.basename(file_path)
    
    # Check file size (error files are typically very small)
    if os.path.getsize(file_path) < 100:
        return True
        
    return any(msg in filename.lower() for msg in error_messages)

def is_valid_subtitle_file(file_path):
    """Check if the file appears to be a valid subtitle file."""
    if not file_path or not os.path.exists(file_path):
        return False
    
    # Check file size (valid subtitle files are typically > 10KB)
    if os.path.getsize(file_path) < 10000:
        return False
    
    # Check file extension
    if not file_path.lower().endswith('.srt'):
        return False
    
    return True

def rename_subtitle_file(downloads_dir, show_name, season, episode, max_retries=3, retry_interval=3):
    """
    Find the latest downloaded file and rename it to match the episode format.
    Includes validation and retry logic.
    """
    attempt = 0
    initial_file_list = set(os.listdir(downloads_dir))
    
    while attempt < max_retries:
        attempt += 1
        
        # Wait for new file to appear
        for _ in range(10):
            time.sleep(1)
            current_files = set(os.listdir(downloads_dir))
            new_files = current_files - initial_file_list
            
            if new_files:
                latest_file = os.path.join(downloads_dir, max(
                    new_files,
                    key=lambda f: os.path.getctime(os.path.join(downloads_dir, f))
                ))
                break
        else:
            continue
            
        # Check if it's an error file
        if is_error_file(latest_file):
            try:
                os.remove(latest_file)
            except:
                pass
            continue
            
        # Check if it's a valid subtitle file
        if not is_valid_subtitle_file(latest_file):
            try:
                os.remove(latest_file)
            except:
                pass
            continue
            
        # Format the new filename
        new_filename = f"{show_name}.S{season:02d}E{episode:02d}.srt"
        new_path = os.path.join(downloads_dir, new_filename)
        
        try:
            # If target file already exists, remove it
            if os.path.exists(new_path):
                os.remove(new_path)
            
            os.rename(latest_file, new_path)
            
            # Final validation
            if os.path.exists(new_path) and is_valid_subtitle_file(new_path):
                return True, new_filename
                
        except:
            continue
            
        time.sleep(retry_interval)
    
    return False, "Download failed" 