# Hand Gesture Particle System

🎨 An interactive particle system controlled by hand gestures using **Three.js**, **MediaPipe**, and real-time camera input.

## ✨ Features

✋ **Hand Gesture Detection**
- Open/close hand gestures to control particle expansion and scaling
- Smooth gesture recognition using MediaPipe Hands
- Real-time camera feed with hand landmark detection

🎭 **Multiple Particle Shapes**
- **Cube** - Classic cubic formation
- **Sphere** - Perfect spherical distribution
- **❤️ Heart** - Beautiful heart-shaped particle pattern
- **🌌 Galaxy** - Spiral galaxy formation
- **🪐 Saturn** - Planet with rings
- **🌸 Flower** - Multi-petal flower design

🎨 **Real-time Customization**
- Color picker for particle color control
- Scale adjustment for particle size
- Expansion speed control
- Particle count slider (100-5000 particles)
- Live FPS and gesture status monitoring

💻 **Modern UI**
- Clean, cyberpunk-style interface with neon colors
- Responsive controls and sliders
- Fullscreen support
- Stats panel with real-time metrics
- Gesture indicator with visual feedback

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/abyxx222/hand-gesture-particle-system.git
   cd hand-gesture-particle-system
   ```

2. **Open in browser**
   - Simply open `index.html` in a modern web browser
   - Allow camera permissions when prompted
   - Ensure good lighting for best gesture detection

3. **Start interacting**
   - Open your hand to expand particles
   - Close your hand to scale down
   - Use the UI panel to customize shapes, colors, and behavior

## 🎮 Controls

### Hand Gestures
- **✋ Open Hand** - Triggers particle expansion explosion
- **✊ Closed Hand** - Contracts particles
- **Spacebar** - Manual explosion trigger

### UI Controls
- **Particle Shape** - Choose from 6 different formations
- **Color Picker** - Select any color for particles
- **Scale Slider** - Adjust particle size (0.5x - 5x)
- **Expansion Speed** - Control expansion force (0.1x - 2x)
- **Particle Count** - Adjust particle density (100 - 5000)
- **Reset** - Reset particles to initial state
- **Fullscreen** - Toggle fullscreen mode

## 📋 Project Structure

```
hand-gesture-particle-system/
├── index.html              # Main HTML file with UI
├── js/
│   ├── particleSystem.js   # Three.js particle rendering
│   ├── gestureDetector.js  # MediaPipe hand detection
│   ├── uiController.js     # UI state management
│   └── app.js              # Main application orchestrator
├── README.md               # This file
└── package.json            # Project dependencies
```

## 🛠 Technologies

- **Three.js** - 3D graphics rendering
- **MediaPipe** - Hand gesture detection
- **WebGL** - Hardware-accelerated graphics
- **Vanilla JavaScript** - No frameworks, pure ES6+

## 📦 External Libraries

```html
<!-- Three.js -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<!-- MediaPipe -->
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js"></script>
```

## 🎯 Performance Optimizations

- **BufferGeometry** - Efficient geometry management
- **PointsMaterial** - Optimized for rendering large particle counts
- **Request Animation Frame** - Smooth 60+ FPS rendering
- **Gesture Debouncing** - Prevents gesture spam
- **Efficient Position Updates** - Direct array manipulation

## 🌐 Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari (iOS 15+)
- Edge

**Requirements:**
- WebGL support
- Camera access permission
- Modern JavaScript (ES6+)

## 📸 Camera Requirements

- Minimum 640x480 resolution recommended
- Good lighting for accurate hand detection
- Clear background for best results
- Camera access must be granted in browser

## 🎨 Customization Guide

### Adding New Particle Shapes

Edit `js/particleSystem.js` and add a new shape generator:

```javascript
case 'yourShape':
    pos = this.yourShapePosition(t);
    break;

yourShapePosition(t) {
    // Return { x, y, z } coordinates
    return {
        x: Math.cos(t * Math.PI * 2) * 8,
        y: Math.sin(t * Math.PI * 2) * 8,
        z: (Math.random() - 0.5) * 8
    };
}
```

### Tweaking Gesture Sensitivity

In `js/gestureDetector.js`, adjust the threshold values:

```javascript
return avgDist > 0.15 && thumbOffset > -0.05; // Adjust these values
```

### Changing Default Colors

Modify the default color in `js/particleSystem.js`:

```javascript
this.color = new THREE.Color(0x00ff88); // Change hex color
```

## 🐛 Troubleshooting

**Camera not working?**
- Check browser permissions
- Try refreshing the page
- Ensure camera is not in use by another application

**Hand gestures not detected?**
- Improve lighting conditions
- Keep hand clearly visible in frame
- Adjust minimum detection confidence in gestureDetector.js

**Low FPS?**
- Reduce particle count
- Close other browser tabs
- Update GPU drivers

## 📝 License

MIT License - Feel free to use this project for personal and commercial purposes.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new particle shapes
- Improve gesture detection
- Enhance UI/UX
- Optimize performance
- Report bugs and suggest features

## 🎉 Credits

- Three.js team for amazing 3D graphics library
- Google MediaPipe for hand detection models
- Community feedback and contributions

---

**Made with ❤️ by abyxx222**

Enjoy playing with particles! 🚀
