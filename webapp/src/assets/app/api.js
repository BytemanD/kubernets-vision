import axios from 'axios';

class Restfulclient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    _parseToQueryString(filters) {
        if (!filters) { return '' }
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
    _getErrorMsg(response){
        let errorData = response.data;
        if (errorData.badRequest && errorData.badRequest.message) {
            return errorData.badRequest.message
        } else {
            return JSON.stringify(errorData)
        }
    }
    async get(url=null) {
        let reqUrl = url ? `${this.baseUrl}/${url}` : this.baseUrl;
        let resp = await axios.get(reqUrl);
        return resp.data
    }
    async delete(id) { let resp = await axios.delete(`${this.baseUrl}/${id}`) ; return resp.data }
    async post(body, url=null) {
        let resp = await axios.post(`${url || this.baseUrl}`, body);
        return resp.data
    }
    async put(id, body) { let resp = await axios.put(`${this.baseUrl}/${id}`, body); return resp.data }
    async show(id, filters={}) {
        let url = filters ? `${id}?${this._parseToQueryString(filters)}` : id;
        let data = await this.get(`${url}`);
        return data
    }
    async list(filters = {}) {
        let queryString = this._parseToQueryString(filters);
        let url = this.baseUrl;
        if (queryString) { url += `?${queryString}` }
        let resp = await axios.get(`${url}`);
        return resp.data;
    }
    async patch(id, body, headers={}){
        let config = {};
        if (headers) { config.headers = headers; }
        let resp = await axios.patch(`${this.baseUrl}/${id}`, body, config);
        return resp.data
    }
    async postAction(id, action, data) {
        let body = {};
        body[action] = data;
        return (await axios.post(`${this.baseUrl}/${id}/action`, body)).data;
    }

    async listActive(){
        return (await this.list({status: 'active'}))
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
class Action extends Restfulclient {
    constructor() { super('/action') }
}
export class Api {
    constructor() {
        this.namespace = new Namespace();
        this.node = new Node();
        this.daemonset = new Daemonset();
        this.deployment = new Deployment();
        this.pod = new Pod();
        this.action = new Action();
    }
}

const API = new Api();

export default API;
