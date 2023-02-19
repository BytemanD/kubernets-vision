import { DaemonsetTable, DeploymentTable, NamespaceTable, NodeTable, PodTable } from "./tables.js";

class BasePage {
    constructor(table){
        this.table = table;
    }
    async refresh(){
        this.table.refresh();
    }
}

export class Overview extends BasePage {
    constructor(){
        super(new NodeTable())
    }
}
export class Namespace extends BasePage {
    constructor(){
        super(new NamespaceTable())
    }
}
export class Deployment extends BasePage {
    constructor(){
        super(new DeploymentTable());
    }
}
export class DeployMentPage extends BasePage {
    constructor(){
        super(new DaemonsetTable());
    }
}
export class Pod extends BasePage{
    constructor(){
        super(new PodTable());
    }
}