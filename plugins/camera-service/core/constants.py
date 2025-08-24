"""Constants for camera service."""

import cv2


# Define supported encoding formats, in the order of recommendation

def getCodecs():
    return [
        {
            'name': 'H264',
            'fourcc': 'mp4v',
            'extension': '.mp4',
            'description': 'H.264/MP4 - Most compatible'
        },
        {
            'name': 'XVID',
            'fourcc': 'XVID',
            'extension': '.avi',
            'description': 'XVID/AVI - Good compatibility'
        },
        {
            'name': 'MJPG',
            'fourcc': 'MJPG',
            'extension': '.avi',
            'description': 'Motion JPEG - High compatibility'
        },
        {
            'name': 'X264',
            'fourcc': 'X264',
            'extension': '.mp4',
            'description': 'X264/MP4 - Modern codec'
        },
        {
            'name': 'H265',
            'fourcc': 'HEVC',
            'extension': '.mp4',
            'description': 'H.265/HEVC - High efficiency'
        },
        {
            'name': 'DIVX',
            'fourcc': 'DIVX',
            'extension': '.avi',
            'description': 'DivX - Legacy support'
        },
        {
            'name': 'RAW',
            'fourcc': 'I420',
            'extension': '.avi',
            'description': 'Raw video - Largest file size'
        }
    ]
