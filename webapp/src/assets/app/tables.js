import API from './api.js'
import { Utils } from './utils';
import { Notify } from "vuetify-message-snackbar";

export class DataTable {
    constructor(headers, api, bodyKey = null, name = '') {
        this.refreshing = false;
        this.headers = headers;
        this.api = api;
        this.bodyKey = bodyKey;
        this.name = name;
        this.itemsPerPage = 10;
        this.search = '';
        this.items = [];
        this.statistics = {};
        this.selected = []
        this.extendItems = []
        this.newItemDialog = null;
        this.namespace = 'default';
    }
    async openNewItemDialog(){
        if (this.newItemDialog){
            this.newItemDialog.open();
        }
    }
    async createNewItem(){
        if (this.newItemDialog) {
            await this.newItemDialog.commit();
            this.refresh();
        }
    }
    async deleteSelected() {
        if (this.selected.length == 0) {
            return;
        }
        this.$MESSAGE.info(`${this.name} 删除中`)
        for (let i in this.selected) {
            let item = this.selected[i];
            try {
                await this.api.delete(item.id || item.name);
                this.waitDeleted(item.id || item.name);
            } catch {
                this.$MESSAGE.error(`删除 ${this.name} ${item.id} 失败`)
            }
        }
        this.$MESSAGE.success('删除完成');
        this.refresh();
        this.resetSelected();
    }
    async waitDeleted(id) {
        let deleted = false;
        while (deleted) {
            let body = await this.api.list({ id: id });
            if (body[this.bodyKey].length == 0) {
                this.$MESSAGE.success(`${this.name} ${id} 删除成功`, 2);
                this.refresh();
                deleted = true;
                continue
            }
            await Utils.sleep(5);
        }
    }
    resetSelected() {
        this.selected = [];
    }
    updateItem(newItem) {
        for (var i = 0; i < this.items.length; i++) {
            if (this.items[i].id != newItem.id) {
                continue;
            }
            for (var key in newItem) {
                this.items[i][key] = newItem[key];
            }
            break
        }
    }
    async refresh(filters = {}) {
        let result = null
        if (this.namespace){
            filters.namespace = this.namespace
        }
        try {
            this.refreshing = true;
            if ( typeof this.api.detail != 'undefined' ) {
                result = await this.api.detail(filters);
            } else {
                result = await this.api.list(filters)
            }
            this.items = this.bodyKey ? result[this.bodyKey] : result;
            return result;
        } catch (e) {
            this.$MESSAGE.error('请求失败')
            console.error(e);
        } finally {
            this.refreshing = false;
        }
    }
    clear(){
        this.items = [];
    }
}
export class NodeTable extends DataTable {
    constructor() {
        super([{ text: '名字', value: 'name' },
               { text: 'Ready', value: 'ready' },
               { text: '内网IP', value: 'internal_ip' },
               { text: '系统', value: 'os_image' },
               { text: '标签', value: 'labels' },
               { text: '操作', value: 'actions' },
            ], API.node, 'nodes', '节点');
            this.extendItems = [
                   { text: '内核版本', value: 'kernel_version' },
                   { text: '容器运行时版本', value: 'container_runtime_version' },
            ]
        this.hideLabels = [
            'beta.kubernetes.io/arch', 'beta.kubernetes.io/os',
            'kubernetes.io/arch', 'kubernetes.io/os', 'kubernetes.io/hostname',
            'node.kubernetes.io/exclude-from-external-load-balancers',
            'node-role.kubernetes.io/control-plane',
        ]
    }
    async deleteLabel(item, label){
        await API.action.post({deleteLabel: {kind: 'node', name: item.name, label: label}});
        Notify.success(`标签 ${label} 删除成功`)
        this.refresh();
    }
}
export class NamespaceTable extends DataTable {
    constructor() {
        super([{ text: '名字', value: 'name' },
               { text: '状态', value: 'status' },
               { text: '标签', value: 'labels' },
              ], API.namespace, 'namespaces', '命名空间');
    }
}
export class DaemonsetTable extends DataTable {
    constructor() {
        super([{ text: '名字', value: 'name' },
               { text: 'Ready', value: 'number_ready' },
               { text: 'available', value: 'number_available' },
               { text: 'current', value: 'current_number_scheduled' },
               { text: 'desired', value: 'desired_number_scheduled' },
               { text: 'node_selector', value: 'node_selector' },
               { text: 'selector', value: 'selector' },
               { text: 'containers', value: 'containers' },
               { text: '操作', value: 'actions' },
            ], API.daemonset, 'daemonsets', '服务守护进程');
        this.extendItems = [
            { text: 'images', value: 'images' },
        ];
    }
}
export class DeploymentTable extends DataTable {
    constructor() {
        super([{ text: '名字', value: 'name' },
               { text: 'Ready', value: 'ready' },
               { text: 'available', value: 'available_replicas' },
               { text: 'containers', value: 'containers' },
          
        ], API.deployment, 'deployments', '服务守护进程');
        this.extendItems = [
            { text: 'images', value: 'images' },
        ];
    }
}
export class PodTable extends DataTable {
    constructor() {
        super([
            { text: '名字', value: 'name' },
            { text: 'node_name', value: 'node_name' },
            { text: 'pod_ip', value: 'pod_ip' },
            { text: 'containers', value: 'containers' },
        ], API.pod, 'pods', 'Pod');
        this.extendItems = [
            { text: 'labels', value: 'labels' },
            { text: 'node_selector', value: 'node_selector' },
            { text: 'containers', value: 'containers' },
        ];
    }
}

export default DataTable;
