library(terra)

tif_folder <- "C:/Users/4saan/Desktop/Mosquito-HSM/WorldClim"
tif_files <- list.files(tif_folder, pattern = "\\.tif$", full.names = TRUE)

illinois_extent <- ext(-91.5, -87.5, 36.9, 42.5)
cropped_rasters <- list()

for (file in tif_files)
{
  raster_layer <- rast(file)
  cropped <- crop(raster_layer, illinois_extent)
  cropped_rasters[[basename(file)]] <- cropped
  cat("Processed:", basename(file), "\n")
}