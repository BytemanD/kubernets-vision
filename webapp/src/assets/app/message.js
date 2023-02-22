import SETTINGS from './settings.js'
import { Notify } from "vuetify-message-snackbar";

export class Message {

    constructor(){
        this.position = SETTINGS.getItem('messagePosition');
    }
    warn(msg) {
        Notify.warning(msg)
    }
    info(msg) {
        Notify.info(msg)
    }
    success(msg) {
        Notify.success(msg)
    }
    error(msg) {
        Notify.error(msg)
    }

}

const MESSAGE = new Message();

export default MESSAGE;

