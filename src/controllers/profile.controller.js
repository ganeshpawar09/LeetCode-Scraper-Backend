import { exec } from "child_process";
import { ApiResponse } from "../utils/ApiResponse.js";
import { ApiError } from "../utils/ApiError.js";

// Function to call the Python script
const scrapeLeetcodeProfile = (username) => {
  return new Promise((resolve, reject) => {
    exec(
      `python src/scripts/scraper.py ${username}`,
      (error, stdout, stderr) => {
        if (error) {
          return reject(
            new ApiError(500, "Error executing Python script", [stderr])
          );
        }
        try {
          const data = JSON.parse(stdout);
          resolve(data);
        } catch (e) {
          reject(new ApiError(500, "Failed to parse JSON", [e.message]));
        }
      }
    );
  });
};

export const profileFetcher = async (req, res) => {
  const { username } = req.query; // Use req.query to get the username

  if (!username) {
    // Handle missing username
    return res.status(400).json(new ApiError(400, "Username is required"));
  }

  try {
    const profileData = await scrapeLeetcodeProfile(username);

    // Ensure statusCode is set correctly
    res
      .status(200)
      .json(
        new ApiResponse(200, profileData, "Profile data fetched successfully")
      );
  } catch (error) {
    if (error instanceof ApiError) {
      // Ensure statusCode is set correctly
      res.status(error.statusCode || 500).json(error);
    } else {
      res.status(500).json(new ApiError(500, "Server error", [error.message]));
    }
  }
};
