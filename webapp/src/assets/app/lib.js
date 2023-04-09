class Dialog {
    constructor(){

    }
    init(){

    }
    commit(){

    }
}

export class DescribeResource extends Dialog{
    constructor(){
        super();
        this.resource = null;
    }
    init(resource){
        this.resource = resource;


    }
    commit(){
        
    }
}
