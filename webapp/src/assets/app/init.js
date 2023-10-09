function Init(){
    var staticStylesheetList = JSON.parse(localStorage.static_stylesheet);
    for (let i in staticStylesheetList){
        var link = document.createElement('link');
        link.setAttribute('rel','stylesheet');
        link.setAttribute('href', staticStylesheetList[i]);
        document.head.appendChild(link);
    }
}
export default Init;