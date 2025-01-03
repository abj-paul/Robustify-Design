import { User } from "./User";


export class Project {
    id : number = 0;
    name : string = "Default";
    description : string = "Default";
    user_id  : number = 0;

    environment_spec : string = "Default";
    system_spec : string = "Default";
    safety_property : string = "Default";
    config : string = "Default";

    user: User = new User();
}