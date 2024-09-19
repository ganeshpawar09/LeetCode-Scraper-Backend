import { Router } from "express";
import { profileFetcher } from "../controllers/profile.controller.js";

const profileRouter = Router();

profileRouter.route("/profile-fetch").get(profileFetcher);

export default profileRouter;
