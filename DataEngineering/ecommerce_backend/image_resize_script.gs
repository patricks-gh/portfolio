function resizeAllImages() {
  const cmToPoints = 28.3465; // 1 cm = 28.3465 points
  const targetHeightCm = 5.4;
  const targetHeightPoints = targetHeightCm * cmToPoints;
  
  const body = DocumentApp.getActiveDocument().getBody();
  const totalImages = body.getImages().length;
  
  let resizedCount = 0;
  
  const images = body.getImages();
  for (let i = 0; i < images.length; i++) {
    const img = images[i];
    const originalHeight = img.getHeight();
    const originalWidth = img.getWidth();
    const aspectRatio = originalWidth / originalHeight;
    
    const newHeight = targetHeightPoints;
    const newWidth = newHeight * aspectRatio;
    
    img.setWidth(newWidth);
    img.setHeight(newHeight);
    resizedCount++;
  }
}
