import express from "express";
import cors from "cors";

const app = express();

app.use(
  cors({
    origin: process.env.CORS_ORIGIN,
    credentials: true,
  })
);
import profileRouter from "./routes/profile.route.js";

app.use("/api/v1/profile", profileRouter);

export { app };
