webpackJsonp([3],{"./src/components/DataWrapper.js":function(e,t,n){"use strict";function r(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function o(e,t){if(!e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return!t||"object"!=typeof t&&"function"!=typeof t?e:t}function a(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function, not "+typeof t);e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,enumerable:!1,writable:!0,configurable:!0}}),t&&(Object.setPrototypeOf?Object.setPrototypeOf(e,t):e.__proto__=t)}function c(e){var t;return Object(i.inject)("store")(t=Object(i.observer)(t=function(t){function n(e){r(this,n);var t=o(this,(n.__proto__||Object.getPrototypeOf(n)).call(this,e));return t.store=t.props.store.appState,t}return a(n,t),l(n,[{key:"componentDidMount",value:function(){this.props.match.url,this.props.match.id&&this.props.match.id}},{key:"componentWillUnmount",value:function(){this.store.clearItems()}},{key:"render",value:function(){return u.a.createElement(e,this.props)}}]),n}(s.Component))||t)||t}t.a=c;var s=n("./node_modules/react/react.js"),u=n.n(s),i=n("./node_modules/mobx-react/index.module.js"),l=(n("./node_modules/react-router-dom/es/index.js"),function(){function e(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}return function(t,n,r){return n&&e(t.prototype,n),r&&e(t,r),t}}())},"./src/components/Protected.js":function(e,t,n){"use strict";function r(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function o(e,t){if(!e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return!t||"object"!=typeof t&&"function"!=typeof t?e:t}function a(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function, not "+typeof t);e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,enumerable:!1,writable:!0,configurable:!0}}),t&&(Object.setPrototypeOf?Object.setPrototypeOf(e,t):e.__proto__=t)}function c(e){var t;return Object(i.inject)("store")(t=Object(i.observer)(t=function(t){function n(e){r(this,n);var t=o(this,(n.__proto__||Object.getPrototypeOf(n)).call(this,e));return t.store=t.props.store.appState,t}return a(n,t),p(n,[{key:"render",value:function(){var t=this.store,n=t.authenticated,r=t.authenticating;return u.a.createElement("div",{className:"authComponent"},n?u.a.createElement(e,this.props):r||n?null:u.a.createElement(l.c,{to:{pathname:"/login",state:{from:this.props.location}}}))}}]),n}(s.Component))||t)||t}t.a=c;var s=n("./node_modules/react/react.js"),u=n.n(s),i=n("./node_modules/mobx-react/index.module.js"),l=n("./node_modules/react-router-dom/es/index.js"),p=function(){function e(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}return function(t,n,r){return n&&e(t.prototype,n),r&&e(t,r),t}}()},"./src/pages/SubPage.js":function(e,t,n){"use strict";function r(e,t){if(!(e instanceof t))throw new TypeError("Cannot call a class as a function")}function o(e,t){if(!e)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return!t||"object"!=typeof t&&"function"!=typeof t?e:t}function a(e,t){if("function"!=typeof t&&null!==t)throw new TypeError("Super expression must either be null or a function, not "+typeof t);e.prototype=Object.create(t&&t.prototype,{constructor:{value:e,enumerable:!1,writable:!0,configurable:!0}}),t&&(Object.setPrototypeOf?Object.setPrototypeOf(e,t):e.__proto__=t)}Object.defineProperty(t,"__esModule",{value:!0}),n.d(t,"default",function(){return m});var c,s=n("./node_modules/react/react.js"),u=n.n(s),i=n("./node_modules/mobx-react/index.module.js"),l=n("./node_modules/react-router-dom/es/index.js"),p=n("./src/components/Protected.js"),f=n("./src/components/DataWrapper.js"),b=function(){function e(e,t){for(var n=0;n<t.length;n++){var r=t[n];r.enumerable=r.enumerable||!1,r.configurable=!0,"value"in r&&(r.writable=!0),Object.defineProperty(e,r.key,r)}}return function(t,n,r){return n&&e(t.prototype,n),r&&e(t,r),t}}(),m=Object(p.a)(c=Object(f.a)(c=Object(i.observer)(c=function(e){function t(e){r(this,t);var n=o(this,(t.__proto__||Object.getPrototypeOf(t)).call(this,e));return n.store=n.props.store,n}return a(t,e),b(t,[{key:"render",value:function(){var e=this,t=this.store.appState.items;return u.a.createElement("div",{className:"page posts"},u.a.createElement("h1",null,"Posts"),u.a.createElement("p",{className:"subheader"},"Posts are fetched from jsonplaceholder.typicode.com"),u.a.createElement("hr",null),u.a.createElement("ul",null,t&&t.length?t.slice(6,12).map(function(t){return u.a.createElement("li",{key:t.id},u.a.createElement(l.b,{to:e.props.match.path+"/"+t.id},u.a.createElement("h1",null,t.title)),u.a.createElement("p",null,t.body.substring(0,120)))}):"Loading..."))}}]),t}(s.Component))||c)||c)||c}});