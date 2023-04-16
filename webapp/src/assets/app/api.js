import axios from 'axios';
import MESSAGE from './message';
import { Utils } from './utils';

class Restfulclient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    _parseToQueryString(filters) {
        if (!filters) { return null }
        let queryParams = [];
        for (var key in filters) {
            if ( Array.isArray(filters[key])){
                console.debug('filters:', filters[key])
                filters[key].forEach(value => {
                    queryParams.push(`${key}=${value}`)
                })
            } else {
                queryParams.push(`${key}=${filters[key]}`)
            }
        }
        return queryParams.join('&');
    }
    _getHeader(){
        return {
            'X-Namespace': Utils.getNamespace(),
        }
    }
    _getErrorMsg(response){
        let errorData = response.data;
        if (errorData.badRequest && errorData.badRequest.message) {
            return errorData.badRequest.message
        } else {
            return JSON.stringify(errorData)
        }
    }
    _alertAndTrow(error){
        if (error.code == 'ERR_NETWORK'){
            MESSAGE.error(`请求失败 ${error.message}`)
        } else if (error.code == 'ERR_BAD_REQUEST'){
            if (typeof error.response == 'string'){
                MESSAGE.error(`请求错误, ${error.response.data}`)
            } else {
                MESSAGE.error(`请求错误, ${error.response.data.error || error.response.data.message}`)
            }
        } else {
            MESSAGE.error(`请求失败 ${error.message}`)
        }
        throw error
    }
    async get(url=null) {
        let reqUrl = url ? `${this.baseUrl}/${url}` : this.baseUrl;
        try {
            let resp = await axios.get(
                reqUrl,
                {headers: this._getHeader()});
            return resp.data;
        } catch (error){
            this._alertAndTrow(error)
        }
    }
    async delete(id) {
        let resp = await axios.delete(
            `${this.baseUrl}/${id}`,
            {headers: this._getHeader()});
        return resp.data
    }
    async post(body, url=null) {
        try{
            let resp = await axios.post(
                `${url || this.baseUrl}`, body,
                {headers: this._getHeader()});
            return resp.data
        } catch (error){
            this._alertAndTrow(error);
        }
    }
    async put(id, body) {
        let resp = await axios.put(
            `${this.baseUrl}/${id}`, body,
            {headers: this._getHeader()});
        return resp.data
    }
    async show(id, filters={}) {
        let url = filters ? `${id}?${this._parseToQueryString(filters)}` : id;
        let data = await this.get(`${url}`);
        return data
    }
    async list(filters = {}) {
        let queryString = this._parseToQueryString(filters);
        let url = queryString ? `?${queryString}`: null;

        try{
            return await this.get(url);
        } catch (error){
            MESSAGE.error(`请求失败 ${error.message}`)
            throw error;
        }
    }
    async patch(id, body, headers={}){
        let config = {};
        if (headers) { config.headers = headers; }
        let resp = await axios.patch(`${this.baseUrl}/${id}`, body, config);
        return resp.data
    }
}

class Namespace extends Restfulclient {
    constructor() { super('/namespace') }
}
class Node extends Restfulclient {
    constructor() { super('/node') }
}
class Daemonset extends Restfulclient {
    constructor() { super('/daemonset') }
}
class Deployment extends Restfulclient {
    constructor() { super('/deployment') }
}
class Pod extends Restfulclient {
    constructor() { super('/pod') }
}
class ConfigMap extends Restfulclient {
    constructor() { super('/configmap') }
}
class Service extends Restfulclient {
    constructor() { super('/service') }
}
class Cronjob extends Restfulclient {
    constructor() { super('/cronjob') }
}
class Job extends Restfulclient {
    constructor() { super('/job') }
}
class Action extends Restfulclient {
    constructor() { super('/action') }

    async execOnPod(name, command, container=null){
        let data = {pod: name, command: command}
        if (container){
            data.container = container;
        }
        return (await this.post({exec: data})).exec
    }
    async getLog(pod, container=null){
        let data = {pod: pod}
        if (container){
            data.container = container;
        }
        return (await this.post({getLog: data})).logs
    }
    async addExecHistory(command, container=null){
        let data = {exec: command}
        if (container){
            data.container = container;
        }
        await this.post({addExecHistory: data})
    }
    async getExecHistory(){
        return (await this.post({getExecHistory: {}})).history
    }
    async getClusterInfo(){
        return (await this.post({getClusterInfo: {}})).cluster_info
    }
}
class Version extends Restfulclient {
    constructor() { super('/version') }
}

export class Api {
    constructor() {
        this.namespace = new Namespace();
        this.node = new Node();
        this.daemonset = new Daemonset();
        this.deployment = new Deployment();
        this.pod = new Pod();
        this.action = new Action();
        this.version = new Version();
        this.configmap = new ConfigMap();
        this.service = new Service();
        this.cronJob = new Cronjob();
        this.job = new Job();
    }
    async addNodeLabels (name, labels){
        await this.action.post({addLabel: {kind: 'node', name: name, labels: labels}});
    }
}

const API = new Api();

export default API;
