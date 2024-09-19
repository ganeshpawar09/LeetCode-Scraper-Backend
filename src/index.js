import { app } from "./app.js";
import dotenv from "dotenv";
dotenv.config({
  path: ".env",
});

app.listen(process.env.PORT || 8000, (err) => {
  if (err) {
    console.error("Error starting server:", err);
    return;
  }
  console.log(`Server is listening on port ${process.env.PORT || 8000}`);
});
