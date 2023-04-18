const KB = 1024;
const MB = KB * 1024;
const GB = MB * 1024;

const namespaceItem = 'namespace';
const defaultNamespace = 'default';


export class Utils {

    static nowFormat(dateObject=null) {
        let date = dateObject ? dateObject : new Date();
        let month = date.getMonth() + 1;
        let day = date.getDate()
        let hours = date.getHours();
        let minutes = date.getMinutes();
        let seconds = date.getSeconds();
        return `${date.getFullYear()}-${month >= 10 ? month : '0' + month}-${day >= 10 ? day : '0' + day} ` +
            `${hours >= 10 ? hours : '0' + hours}:${minutes >= 10 ? minutes : '0' + minutes}:${seconds >= 10 ? seconds : '0' + seconds}`;
    }
    static parseUTCToLocal(utcString){
        if (! utcString) {
            return '';
        }
        if (! utcString.endsWith('Z')){
            utcString += 'Z'
        }
        return Utils.nowFormat(new Date(`${utcString}`))
    }
    static getRandomName(prefix = null) {
        let date = this.nowFormat()
        return prefix ? `${prefix}-${date}` : date;
    }

    static humanRam(size) {
        if (size < 1024) {
            return `${size} MB`
        }
        return `${(size / 1024).toFixed(0)} GB`
    }
    static humanSize(size) {
        if (size == null){
            return ''
        } else if (size <= KB) {
            return `${size} B`
        } else if (size <= MB) {
            return `${(size / KB).toFixed(2)} KB`
        } else if (size <= GB) {
            return `${(size / MB).toFixed(2)} MB`
        } else {
            return `${(size / GB).toFixed(2)} GB`
        }
    }
    static sleep(seconds) {
        seconds = (seconds || 0);
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                resolve(true);
                console.debug(reject)
            }, seconds * 1000)
        })
    }
    static copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
        } else {
            let element = document.createElement('input', text)
            element.setAttribute('value', text);
            document.body.appendChild(element)
            element.select();
            document.execCommand('copy');
            document.body.removeAttribute(element);
        }
    }
    static lastDateList(steps, nums){
        // Get last n list of date
        // e.g. [timestamp1, timestamp2, ...]
        let endDate = new Date();
        let dateList = [];
        for (let i = 0; i < nums; i++){
            for (let unit in steps) {
                switch (unit) {
                    case 'hour':
                        endDate.setHours(endDate.getHours() - steps.hour);
                        break;
                    case 'month':
                        endDate.setMonth(endDate.getMonth() - steps.month)
                        break;
                    case 'day':
                        endDate.setDate(endDate.getDate() - steps.day);
                        break;
                    case 'year':
                        endDate.setFullYear(endDate.getFullYear() - steps.year);
                        break;
                    default:
                        throw Error(`Invalid step unit ${unit}`);
                }
            }
            dateList.push(endDate.getTime());
        }
        return dateList.reverse();
    }
    static getConainerCmd(container){
        let command = container.command ? container.command.join(' ') : ''
        let args = container.args ? container.args.join(' ') : ''
        return `${command} ${args}`
    }
    static getPodReadyNum(pod){
        let nums = 0
        for (let i in pod.container_statuses){
            let status = pod.container_statuses[i];
            if (status.ready){
                nums += 1
            }
        }
        return nums
    }
    static getPodWaiting(pod){
        let waiting = {};
        for (let i in pod.container_statuses){
            let status = pod.container_statuses[i];
            if (status.state.waiting){
                waiting = status.state.waiting;
                break;
            }
        }
        return waiting;
    }

    static getNamespace(){
        return sessionStorage.getItem(namespaceItem) || defaultNamespace;
    }
    static setNamespace(namespace){
        sessionStorage.setItem(namespaceItem, namespace);
    }
    static parseNodeMemory(memory){
        if (memory.endsWith('Ki')){
            let ki = parseInt(memory.slice(0, -2))
            return `${(ki / 1024 / 1024).toFixed(2)} GB`
        } else {
            return memory
        }
    }
    static getNavigationSelectedItem(){
        let localItem = localStorage.getItem('navigationSelectedItem');
        return localItem ? JSON.parse(localItem): null;
    }
    static setNavigationSelectedItem(item){
        localStorage.setItem('navigationSelectedItem', JSON.stringify(item));
    }

}
