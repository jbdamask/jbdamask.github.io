---
title: Image Object Remover
tool_url: /tools/image-object-remover.html
excerpt: Paint over unwanted elements in an image and remove them, filling in the background automatically
permalink: /tools/image-object-remover/
---

# Image Object Remover

A client-side tool for removing unwanted elements from images. Paint over logos, text, watermarks, or other objects and the tool fills in the area using surrounding pixels.

## Features

### Image Input
- **Drag & Drop**: Drop images directly onto the page
- **File Picker**: Click to select images from your device

### Mask Painting
- **Adjustable Brush**: Slider to control brush size (5–80px)
- **Visual Preview**: Brush cursor preview follows your mouse
- **Red Overlay**: Painted mask is shown as a semi-transparent red highlight
- **Undo**: Step back through brush strokes
- **Clear Mask**: Reset the mask and start over

### Inpainting Algorithm
- **Onion-Peel Fill**: Fills the masked region from the outside in, layer by layer, using only known (non-masked) pixel values as sources
- **Smoothing Pass**: Applies additional averaging passes to eliminate banding artifacts
- **Progress Indicator**: Visual progress bar during processing

### Export
- **PNG Download**: Save the result as a PNG file

## Usage

1. Open the tool and upload an image
2. Adjust the brush size as needed
3. Paint over the element you want to remove
4. Click "Remove Selection"
5. Download the result

## Limitations

This uses a simple client-side diffusion algorithm. It works best for:
- Small to medium elements on relatively uniform backgrounds
- Logos, watermarks, and text on gradients or solid colors

For complex scenes or large removals, an AI-based inpainting service would produce better results.

## Technical Implementation

- **No Dependencies**: Single HTML file with embedded CSS and JavaScript
- **Canvas API**: Separate canvases for the image and mask overlay
- **Client-Side Processing**: All computation runs in the browser — no server or API calls
- **Non-blocking**: Uses `requestAnimationFrame` to keep the UI responsive during processing
