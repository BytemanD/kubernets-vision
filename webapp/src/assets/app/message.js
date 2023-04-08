import Vue from "vue";

export class Message {
    constructor(position) {
        let positionXY = position.split('-');
        this.y = positionXY[0];
        this.x = positionXY[1];
        this.notify = Vue.prototype.$toast;
    }
    info(msg) {
        this.notify(msg, { x: this.x, y: this.y, color: 'info', timeout: 1000, icon: 'mdi-information' });
    }
    success(msg) {
        this.notify(msg, { x: this.x, y: this.y, color: 'success', timeout: 1000, icon: 'mdi-check-circle' });
    }
    warning(msg) {
        this.notify(msg, { x: this.x, y: this.y, color: 'warning', icon: 'mdi-alert-circle' });
    }
    error(msg) {
        this.notify(msg, { x: this.x, y: this.y, color: 'error', icon: 'mdi-close-circle' });
    }
}

const MESSAGE = new Message('bottom-right');

export default MESSAGE;

