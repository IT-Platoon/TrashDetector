class Mode:
    EMPTY: str = ""
    VIDEO: str = "video"
    IMAGE: str = "image"
    WEBCAM: str = "webcam"


FUNCTIONS = {
    Mode.EMPTY: None,
    Mode.IMAGE: "run_detection_images",
    Mode.VIDEO: "run_detection_videos",
    Mode.WEBCAM: "run_detection_webcam",
}
