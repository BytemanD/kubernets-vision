import SETTINGS from './settings.js'

export class Message {

    constructor(){
        this.position = SETTINGS.getItem('messagePosition');
    }
    warn(msg) {
        console.log('WARNING', msg)
    }
    info(msg) {
        console.log('INFO', msg)
    }
    success(msg) {
        console.log('SUCCESS', msg)
    }
    error(msg) {
        console.log('ERROR', msg)
    }

}

const MESSAGE = new Message();

export default MESSAGE;

