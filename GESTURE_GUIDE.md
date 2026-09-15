# Gesture Detection Threshold Guide

## Hand Open Detection Algorithm

The gesture detection uses finger extension distance from palm center.

### Current Parameters

```javascript
avgDist > 0.15    // Average finger extension distance
thumbOffset > -0.05  // Thumb position offset
gestureDebounce = 100ms  // Time between gesture changes
```

### Sensitivity Levels

**High Sensitivity (Easy to trigger)**
```javascript
return avgDist > 0.12 && thumbOffset > -0.08;
gestureDebounce = 50;
```

**Medium Sensitivity (Recommended)**
```javascript
return avgDist > 0.15 && thumbOffset > -0.05;
gestureDebounce = 100;
```

**Low Sensitivity (Hard to trigger)**
```javascript
return avgDist > 0.18 && thumbOffset > -0.02;
gestureDebounce = 150;
```

## Landmark References

- **0** - Wrist
- **1-4** - Thumb (4 = tip)
- **5-8** - Index (8 = tip)
- **9-12** - Middle (12 = tip)
- **13-16** - Ring (16 = tip)
- **17-20** - Pinky (20 = tip)

## Testing Gesture Detection

1. Open browser console (F12)
2. Check gesture logs in gesture detector
3. Monitor `isHandOpen` value in UI stats
4. Adjust thresholds based on your environment

## Performance Tips

- Increase debounce time for noisy detection
- Improve lighting for stable landmarks
- Test in controlled environment first
- Use different threshold for left/right hands if needed
