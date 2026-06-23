import { S3Client, PutObjectCommand } from "@aws-sdk/client-s3";
import { createReadStream, readdirSync, statSync, createWriteStream } from "fs";
import * as path from "path";
import fetch from "node-fetch";
import { NodeHttpHandler } from "@smithy/node-http-handler";

const cesiumUrl = "https://api.cesium.com/v1";
const authToken = process.env.CESIUM_AUTH_TOKEN;

interface CesiumAsset {
  id?: number;
  archiveId?: number;
  name?: string;
  description?: string;
  type?: "3DTILES";
  options?: {
    sourceType: "3D_MODEL";
    geometryCompression: "NONE";
  };
}

const createNewAssetHandler = async (event: CesiumAsset) => {
  console.log(authToken);
  console.log(JSON.stringify({
    name: event.name,
    description: event.description,
    type: event.type,
    options: event.options
  }));
  try {
    const response = await fetch(`${cesiumUrl}/assets`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        name: event.name,
        description: event.description,
        type: event.type,
        options: event.options
      }),
    });

    if (!response.ok) {
      console.error(response);
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const responseData = await response.json();
    return responseData;
  } catch (error) {
    console.error("Error posting JSON data: ", error);
    throw error;
  }
};

const notifyUploadCompleteHandler = async (event: CesiumAsset) => {
  try {
    const response = await fetch(
      `${cesiumUrl}/assets/${event.id}/uploadComplete`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      }
    );
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return response;
  } catch (error) {
    console.error("Error posting JSON data: ", error);
    throw error;
  }
};

const getStatusHandler = async (event: CesiumAsset) => {
  try {
    const response = await fetch(`${cesiumUrl}/assets/${event.id}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const responseData = await response.json();
    return responseData;
  } catch (error) {
    console.error("Error posting JSON data: ", error);
    throw error;
  }
};

const createArchiveHandler = async (event: CesiumAsset) => {
  try {
    const response = await fetch(`${cesiumUrl}/archives`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        assetIds: [event.id],
        format: "ZIP",
        type: "FULL",
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const responseData = await response.json();
    return responseData;
  } catch (error) {
    console.error("Error posting JSON data: ", error);
    throw error;
  }
};

const getArchiveStatusHandler = async (event: CesiumAsset) => {
  try {
    const response = await fetch(`${cesiumUrl}/archives/${event.archiveId}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    // Parse the JSON response
    const responseData = await response.json();
    return responseData;
  } catch (error) {
    console.error("Error posting JSON data:", error);
    throw error;
  }
};

const downloadArchiveHandler = async (
  event: CesiumAsset,
  downloadURL: string
) => {
  try {
    const response = await fetch(
      `${cesiumUrl}/archives/${event.archiveId}/download`,
      {
        method: "GET",
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const writer = createWriteStream(downloadURL);
    await response.body.pipe(writer);
  } catch (error) {
    console.error("Error posting JSON data:", error);
    throw error;
  }
};

const create3DTiles = async (
  name: string,
  description: string,
  inputDir: string,
  downloadFile: string
) => {
  const createNewAssetResult: any = await createNewAssetHandler({
    name: name,
    description: description,
    type: "3DTILES",
    options: { sourceType: "3D_MODEL", geometryCompression: "NONE" },
  });

  const AWS_ACCESS_KEY_ID = createNewAssetResult.uploadLocation.accessKey;
  const AWS_SECRET_ACCESS_KEY =
    createNewAssetResult.uploadLocation.secretAccessKey;
  const SESSION_TOKEN = createNewAssetResult.uploadLocation.sessionToken;
  const AWS_REGION = "us-east-1";
  const BUCKET_NAME = createNewAssetResult.uploadLocation.bucket;

  console.log(AWS_SECRET_ACCESS_KEY);

  // Create an S3 client
  const s3Client = new S3Client({
    region: AWS_REGION,
    credentials: {
      accessKeyId: AWS_ACCESS_KEY_ID,
      secretAccessKey: AWS_SECRET_ACCESS_KEY,
      sessionToken: SESSION_TOKEN,
    },
    requestHandler: new NodeHttpHandler({
      connectionTimeout: 10000,
      requestTimeout: 10000,
    })
  });

  const dir = inputDir;
  const files = readdirSync(dir);

  for (const file of files) {
    console.log(file);
    try {
      const filePath = path.join(dir, file);

      // Ensure the path is a file (not a directory)
      if (statSync(filePath).isFile()) {
        console.log(filePath);
        const fileStream = createReadStream(filePath);
        const uploadParams = {
          Bucket: BUCKET_NAME,
          Key: `sources/${createNewAssetResult.assetMetadata.id}/${file}`, // The name of the file (or path in the bucket)
          Body: fileStream,
        };
        const command = new PutObjectCommand(uploadParams);
        console.log(command);
        const fileUploadResult = await s3Client.send(command);

      }
    } catch (e) {
      console.error(e);
    }
  }

  const notifyUploadCompleteResult = await notifyUploadCompleteHandler({
    id: createNewAssetResult.assetMetadata.id,
  });
  console.log(notifyUploadCompleteResult);

  let statusResult: any = await getStatusHandler({
    id: createNewAssetResult.assetMetadata.id,
  });
  console.log(statusResult);

  while (statusResult.status != "COMPLETE") {
    statusResult = await getStatusHandler({
      id: createNewAssetResult.assetMetadata.id,
    });
    console.log(statusResult);
  }

  let createArchiveResult: any = await createArchiveHandler({
    id: createNewAssetResult.assetMetadata.id,
  });
  console.log(createArchiveResult);

  let archiveStatusResult: any = await getArchiveStatusHandler({
    archiveId: createArchiveResult.id,
  });
  console.log(archiveStatusResult);

  while (archiveStatusResult.status != "COMPLETE") {
    archiveStatusResult = await getArchiveStatusHandler({
      archiveId: createArchiveResult.id,
    });
    console.log(archiveStatusResult);
  }

  const downloadResult = await downloadArchiveHandler(
    { archiveId: createArchiveResult.id },
    downloadFile
  );
  console.log(downloadResult);
};

const args = process.argv.slice(2);

console.log(args);

create3DTiles(
  args[0],
  args[1],
  args[2],
  args[3]
);
