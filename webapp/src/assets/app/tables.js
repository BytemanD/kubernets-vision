import API from './api.js'
import MESSAGE from './message.js';
import { Utils } from './utils';

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
        for (let i in this.selected) {
            let item = this.selected[i];
            try {
                MESSAGE.info(`${this.name} ${item.name} 删除中`)
                await this.api.delete(item.id || item.name);
                this.waitDeleted(item.id || item.name);
            } catch {
                MESSAGE.error(`${this.name} ${item.name} 删除失败`)
            }
        }

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
        MESSAGE.success('删除完成');
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
               { text: 'CPU', value: 'cpu' },
               { text: '内存', value: 'memory' },
               { text: '系统', value: 'os_image' },
               { text: '创建时间', value: 'creation' },
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
        MESSAGE.success(`标签 ${label} 删除成功`)
        this.refresh();
    }
}
export class NamespaceTable extends DataTable {
    constructor() {
        super([{ text: '名字', value: 'name' },
               { text: '状态', value: 'status' },
               { text: '标签', value: 'labels' },
               { text: '创建时间', value: 'creation' },
               { text: '操作', value: 'actions' },
              ], API.namespace, 'namespaces', '命名空间');
    }
}
export class DaemonsetTable extends DataTable {
    constructor() {
        super([{ text: '名字', value: 'name' },
               { text: 'Ready', value: 'ready' },
               { text: 'available', value: 'number_available' },
               { text: 'current', value: 'current_number_scheduled' },
            //    { text: 'Ready', value: 'number_ready' },
            //    { text: 'desired', value: 'desired_number_scheduled' },
               { text: 'node_selector', value: 'node_selector' },
               { text: 'selector', value: 'selector' },
               { text: 'containers', value: 'containers' },
               { text: '创建时间', value: 'creation' },
               { text: '操作', value: 'actions' },
            ], API.daemonset, 'daemonsets', '服务守护进程');
            this.extendItems = [];
    }
}
export class DeploymentTable extends DataTable {
    constructor() {
        super([{ text: '名字', value: 'name' },
               { text: 'Ready', value: 'ready' },
               { text: 'available', value: 'available_replicas' },
               { text: 'containers', value: 'containers' },
               { text: '创建时间', value: 'creation' },
               { text: '操作', value: 'actions' },
        ], API.deployment, 'deployments', '服务守护进程');
        this.extendItems = [
            // { text: 'images', value: 'images' },
        ];
    }
}
export class PodTable extends DataTable {
    constructor() {
        super([
            { text: '名字', value: 'name' },
            { text: '就绪', value: 'ready' },
            { text: '阶段', value: 'phase' },
            { text: '状态', value: 'state' },
            { text: '所在节点', value: 'node_name' },
            { text: 'IP地址', value: 'pod_ip' },
            { text: 'containers', value: 'containers' },
            { text: '创建时间', value: 'creation' },
            { text: '操作', value: 'actions' },
        ], API.pod, 'pods', '容器组');
        this.extendItems = [
            { text: 'labels', value: 'labels' },
            { text: 'node_selector', value: 'node_selector' },
            { text: 'containers', value: 'containers' },
        ];
        this.waiting = {};
    }
    updateWaiting(pod){
        this.waiting[pod.name] = Utils.getPodWaiting(pod);
    }
}
export class ConfigMapTable extends DataTable {
    constructor() {
        super([{ text: '名字', value: 'name' },
               { text: '数据个数', value: 'data_nums' },
               { text: '创建时间', value: 'creation' },
               { text: '操作', value: 'actions' },
            ], API.configmap, 'configmaps', '配置字典');
            this.extendItems = [
                   { text: '数据', value: 'data_list' },
            ]
    }
}
export class SecretTable extends DataTable {
    constructor() {
        super([{ text: '名字', value: 'name' },
               { text: '数据个数', value: 'data_nums' },
               { text: '创建时间', value: 'creation' },
               { text: '操作', value: 'actions' },
            ], API.secret, 'secrets', '加密数据');
            this.extendItems = [
                   { text: '数据', value: 'data_list' },
            ]
    }
}
export class ServiceTable extends DataTable {
    constructor() {
        super([{ text: '名字', value: 'name' },
               { text: '类型', value: 'type' },
               { text: 'IP', value: 'cluster_ip' },
               { text: 'IP列表', value: 'cluster_i_ps' },
               { text: 'IP栈', value: 'ip_families' },
               { text: '端口', value: 'ports' },
               { text: '创建时间', value: 'creation' },
               { text: '操作', value: 'actions' },
            ], API.service, 'services', '服务');
            this.extendItems = [
                   { text: '数据', value: 'data_list' },
            ]
    }
}
export class CronjobTable extends DataTable {
    constructor() {
        super([{ text: '名字', value: 'name' },
               { text: 'node_selector', value: 'node_selector' },
               { text: 'selector', value: 'selector' },
               { text: 'containers', value: 'containers' },
               { text: '创建时间', value: 'creation' },
               { text: '创建时间', value: 'creation' },
            ], API.cronJob, 'cronjobs', '定时任务');
            this.extendItems = [
                   { text: '数据', value: 'data_list' },
            ]
    }
}
export class JobTable extends DataTable {
    constructor() {
        super([{ text: '名字', value: 'name' },
               { text: 'node_selector', value: 'node_selector' },
               { text: 'selector', value: 'selector' },
               { text: 'containers', value: 'containers' },
               { text: '创建时间', value: 'creation' },
            ], API.job, 'jobs', '任务');
            this.extendItems = [
                   { text: '数据', value: 'data_list' },
            ]
    }
}
export default DataTable;
