/**
 * Gesture Detector - Detects hand open/close using MediaPipe Hands
 */
class GestureDetector {
    constructor(videoElement, onHandOpen, onHandClosed) {
        this.videoElement = videoElement;
        this.onHandOpen = onHandOpen;
        this.onHandClosed = onHandClosed;
        this.hands = null;
        this.camera = null;
        this.isHandOpen = false;
        this.lastGestureTime = 0;
        this.gestureDebounce = 100; // ms
        
        this.init();
    }

    async init() {
        try {
            this.hands = new Hands({
                locateFile: (file) => {
                    return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
                }
            });

            this.hands.setOptions({
                maxNumHands: 2,
                modelComplexity: 1,
                minDetectionConfidence: 0.5,
                minTrackingConfidence: 0.5
            });

            this.hands.onResults((results) => this.onResults(results));

            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.setupCamera());
            } else {
                this.setupCamera();
            }
        } catch (error) {
            console.error('Error initializing gesture detector:', error);
        }
    }

    setupCamera() {
        this.camera = new Camera(this.videoElement, {
            onFrame: async () => {
                try {
                    await this.hands.send({ image: this.videoElement });
                } catch (error) {
                    console.error('Error sending frame to hands:', error);
                }
            },
            width: this.videoElement.videoWidth || 1280,
            height: this.videoElement.videoHeight || 720
        });

        this.camera.start();
    }

    onResults(results) {
        if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
            for (let hand of results.multiHandLandmarks) {
                const isOpen = this.isHandOpen(hand);
                const now = Date.now();

                if (isOpen !== this.isHandOpen && now - this.lastGestureTime > this.gestureDebounce) {
                    this.isHandOpen = isOpen;
                    this.lastGestureTime = now;

                    if (isOpen) {
                        this.onHandOpen();
                    } else {
                        this.onHandClosed();
                    }
                }
            }
        }
    }

    isHandOpen(landmarks) {
        // Get finger tip positions
        const indexTip = landmarks[8];      // Index finger
        const middleTip = landmarks[12];    // Middle finger
        const ringTip = landmarks[16];      // Ring finger
        const pinkyTip = landmarks[20];     // Pinky finger
        const thumbTip = landmarks[4];      // Thumb

        // Get palm position
        const wrist = landmarks[0];
        const palmCenter = landmarks[9];

        // Calculate distances from palm to fingers
        const indexDist = this.distance(indexTip, palmCenter);
        const middleDist = this.distance(middleTip, palmCenter);
        const ringDist = this.distance(ringTip, palmCenter);
        const pinkyDist = this.distance(pinkyTip, palmCenter);
        const thumbDist = this.distance(thumbTip, palmCenter);

        // Average distance
        const avgDist = (indexDist + middleDist + ringDist + pinkyDist) / 4;
        const thumbOffset = thumbDist - 0.02;

        // Hand is open if fingers are extended (large average distance)
        return avgDist > 0.15 && thumbOffset > -0.05;
    }

    distance(point1, point2) {
        const dx = point1.x - point2.x;
        const dy = point1.y - point2.y;
        const dz = point1.z - point2.z;
        return Math.sqrt(dx * dx + dy * dy + dz * dz);
    }

    setDebounce(ms) {
        this.gestureDebounce = ms;
    }
}
