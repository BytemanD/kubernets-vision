const KB = 1024;
const MB = KB * 1024;
const GB = MB * 1024;

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
}