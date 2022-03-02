let origin = window.location.origin
let pathname = window.location.pathname.replaceAll('/reports','')

var environment = {
    api_url:`${origin}${pathname}`
};