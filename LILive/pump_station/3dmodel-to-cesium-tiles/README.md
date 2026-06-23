## 3D Model to Cesium Tiles

This repository contains a simple script that orchestrates the calls necessary to the 
[Cesium ion REST API](https://cesium.com/learn/ion/rest-api/) in order to convert a 3D model
to Cesium 3D tile format.

It has been tested on both GLB files (up to 300MB) as well as OBJ files and associated textures
such as are produced by photogrammetry software such as [Drone Deploy](https://www.dronedeploy.com/).

Before running the script, please ensure you have a Cesium ion account setup and have configured an [access token](https://ion.cesium.com/tokens) with the necessary scopes to create andd export assets.

You provide the script an input directory containing a 3D model in OBJ or GLB/GLTF format, an output directory
and a name and description for the Cesium Ion asset. 

The script has been tested against NodeJS 22.13.0 - please ensure you have this installed first, and well as NPM.

### Building and executing
Set an environment variable containing your Cesium ion access token with the command

```
export CESIUM_AUTH_TOKEN=eyJ.....
```

To run the script, first install dependencies by running the following command

```
npm ci
```

Then you can build the Typescript file to JS by running the command

```
./node_modules/typescript/bin/tsc cesiumTiler.ts
```

Finally you can run the Javascript file with Node with the following command, providing a name and description for the asset that will be created in Cesium ion, the directory containing your 3D model, and a directory to output the zipped 3D tiles to.

⚠️ Ensure that the files in the source directory are readable before running the command (e.g. ```chmod -R +r <directory>```)

```
node cesiumTiler.js AssetName AssetDescription <path_to_dir_containing_3d_model> <path_to_output_dir/filename.zip>
```

Once the script completes, the 3D tiles will be available in the output directory / filename specified 