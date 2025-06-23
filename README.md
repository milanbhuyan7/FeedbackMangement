# 3D Object Reconstruction from Webcam

This project is an AI-powered web-based agent that captures video through a webcam, detects and segments real-world objects, estimates depth, reconstructs 3D models in real-time or near-real-time, and renders them using WebGL (Three.js).

## Project Objective

To build a modular pipeline for 3D reconstruction from monocular video input with the following components:

1. **Camera Input**: Use webcam via WebRTC to capture frames
2. **Object Detection**: Identify and segment object(s) of interest
3. **Depth Estimation**: Use monocular depth model to get depth map
4. **3D Point Cloud Builder**: Convert RGB + Depth to 3D points
5. **Point Cloud Fusion** (Optional): Align and fuse multiple frames (ICP or SLAM)
6. **Mesh Generation**: Generate mesh from point cloud (Poisson or surface nets)
7. **WebGL Rendering**: Render point cloud or mesh using Three.js
8. **Object Classification** (Optional): Identify object type using AI model
9. **Save/Export** (Optional): Export to OBJ/GLB for reuse or analysis

## Tech Stack

### Frontend
- **Framework**: React with TypeScript
- **Build Tool**: Vite
- **Webcam Access**: react-webcam (WebRTC / MediaDevices API)
- **AI Models**: TensorFlow.js for object detection, segmentation, depth
- **3D Rendering**: Three.js for WebGL rendering

### AI Models
- **Object Detection**: COCO-SSD
- **Depth Estimation**: MiDaS
- **Mesh Generation**: Basic convex hull (simplified implementation)

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── CameraInput.tsx       # Webcam capture module
│   │   ├── ObjectDetection.tsx   # Object detection using COCO-SSD
│   │   ├── DepthEstimation.tsx   # Depth map generation using MiDaS
│   │   ├── PointCloudBuilder.tsx # 3D point cloud from RGB-D
│   │   ├── MeshGeneration.tsx    # Mesh generation from point cloud
│   │   ├── Renderer3D.tsx        # Three.js visualization
│   │   └── PipelineStatus.tsx    # Pipeline status display
│   ├── App.tsx                   # Main application component
│   ├── main.tsx                  # Entry point
│   └── ...
└── ...
```

## Getting Started

### Prerequisites
- Node.js (v14 or later)
- npm or yarn

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd MTech_Project
```

2. Install dependencies
```bash
cd frontend
npm install
```

3. Start the development server
```bash
npm run dev
```

4. Open your browser and navigate to `http://localhost:5173`

## Usage

1. Click "Start Camera" to activate your webcam
2. The system will automatically load the required AI models
3. Click "Start Continuous Capture" to begin processing frames
4. Objects will be detected, depth will be estimated, and a 3D reconstruction will be generated
5. Use your mouse to rotate, pan, and zoom the 3D view
6. Toggle between point cloud and mesh visualization
7. Export the model when satisfied with the result

## Limitations

- Monocular depth estimation is less accurate than stereo or LiDAR-based methods
- Real-time performance depends on your hardware capabilities
- Complex or reflective objects may not reconstruct well
- The simplified mesh generation algorithm may not capture fine details

## Future Improvements

- Implement more sophisticated mesh generation algorithms (Poisson surface reconstruction)
- Add support for point cloud fusion across multiple frames
- Improve object segmentation with more advanced models
- Add texture mapping to the reconstructed mesh
- Implement server-side processing for more complex models

## License

[MIT License](LICENSE)