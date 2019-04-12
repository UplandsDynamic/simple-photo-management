/* react */
import React from 'react';
/* app components */
import Header from './header.js';
import Message from './message.js';
import Footer from './footer.js';
import DataTable from './data-table';
/* functions */
import processRequest from "./api";
/* cookies */
import Cookies from 'js-cookie';
/* axios */
import axios from 'axios/index';
/* css */
import './css/index.css';
/* font awesome icons */
import {library} from '@fortawesome/fontawesome-svg-core'
import {
    faSyncAlt, faEllipsisH, faPlus, faPlusSquare, faMinus, faMinusSquare,
    faTrashAlt, faEdit, faTruck
} from '@fortawesome/free-solid-svg-icons'

library.add(faSyncAlt, faEllipsisH, faPlus, faTrashAlt, faEdit, faPlusSquare, faMinus, faMinusSquare, faTruck);


axios.defaults.withCredentials = true;

/* App root */
class App extends React.Component {

    constructor(props) {
        super(props); // makes 'this' refer to component (i.e. like python self)
        /* set local state. Only initialise stockData with required defaults for 1st request and
        BEFORE data returned. Rest all added in call to stockDataHandler called after response received
        */
        this.apiOptions = {
            /* used to define available API options in the api-request component */
            GET_PHOTOS: {requestType: 'get_photos', method: 'GET', desc: 'request to get photo data'},
            PATCH_STOCK: {requestType: 'patch_stock', method: 'PATCH', desc: 'PATCH request to update stock data'},
            ADD_STOCK: {requestType: 'add_stock', method: 'POST', desc: 'POST request to add stock data'},
            DELETE_STOCK_LINE: {
                requestType: 'delete_stock_line',
                method: 'DELETE',
                desc: 'DELETE request to delete stock line'
            },
            POST_AUTH: {requestType: 'post_auth', method: 'POST', desc: 'POST request to for authorization'},
            PATCH_CHANGE_PW: {
                requestType: 'patch_change_pw',
                method: 'PATCH',
                desc: 'PATCH request to for changing password'
            },
        };
        this.initialState = {
            record: {
                meta: {
                    page: 1,
                    limit: process.env.REACT_APP_ROWS_PER_TABLE,
                    pagerMainSize: process.env.REACT_APP_PAGER_MAIN_SIZE,
                    pagerEndSize: process.env.REACT_APP_PAGER_END_SIZE,
                    pageOrderBy: '',
                    pageOrderDir: '',
                    previous: null,
                    next: null,
                    cacheControl: 'no-cache',  // no caching by default, so always returns fresh data
                    search: ''
                },
                data: {
                    results: [],
                    updateData: {}
                }
            },
            authMeta: {
                authenticated: false,
                userIsAdmin: false,
            },
            message: null,
            messageClass: '',
            greeting: process.env.REACT_APP_GREETING,
            csrfToken: null,
        };
        this.state = JSON.parse(JSON.stringify(this.initialState));
    }

    componentDidMount() {
        this.setState({csrfToken: this.getCSRFToken()});
        // kick off: attempt to authenticate (new authentication also requests stock data)
        this.setAuthentication();
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
    }

    getCSRFToken = () => {
        return Cookies.get('csrftoken')
    };

    setSessionStorage = ({key, value}) => {
        sessionStorage.setItem(key, value);
    };

    getSessionStorage = (key) => {
        //return JSON.parse(localStorage.getItem(key));
        return sessionStorage.getItem(key);
    };

    deleteSessionStorage = (keys = []) => {
        if (keys.length > 0) {
            keys.forEach((k) => {
                sessionStorage.removeItem(k)
            })
        }
        return true;
    };

    setAuthentication = () => {
        let authenticated = !!this.getSessionStorage('token');
        let clonedAuthMeta = JSON.parse(JSON.stringify(this.state.authMeta));
        Object.assign(clonedAuthMeta, {authenticated});
        // set authentication state and fetch new stock records when done (in a callback)
        this.setState({authMeta: {...clonedAuthMeta}}, this.getRecordsHandler);
    };

    setAuthorized = ({role = 'admin', state = false} = {}) => {
        // called after each api response returning stock data
        let clonedAuthMeta = JSON.parse(JSON.stringify(this.state.authMeta));
        if (role === 'admin') {
            Object.assign(clonedAuthMeta, {userIsAdmin: state});
        }
        this.setState({authMeta: {...clonedAuthMeta}});
    };

    setRecordState = ({newRecord} = {}) => {
        /*
        method to update state for record being retrieved (GET request)
         */
        let {page} = newRecord.meta;
        if (newRecord) {
            // ensure page never < 1
            let updatedPage = page < 1 ? 1 : page;
            Object.assign(newRecord.meta, {page: updatedPage});
            // set user admin status to what was returned from api in stock record data
            if (!!newRecord.data.results.length && newRecord.data.results[0].hasOwnProperty('user_is_admin')
            ) {
                this.setAuthorized({role: 'admin', state: !!newRecord.data.results[0].user_is_admin})
            }
        }
        this.setState({record: newRecord});
    };

    getRecordsHandler = ({record = this.state.record, url = null, notifyResponse = true} = {}) => {
        if (this.state.authMeta.authenticated) {
            const apiRequest = processRequest({
                url: url,
                record: record,
                apiMode: this.apiOptions.GET_PHOTOS
            });
            if (apiRequest) {
                apiRequest.then((response) => {
                    if (response) {
                        if (notifyResponse) {
                            this.setMessage({
                                message: 'Records successfully retrieved!',
                                messageClass: 'alert alert-success'
                            });
                        }
                        Object.assign(record.data, {...response.data});
                        Object.assign(record.meta, {...record.meta});
                        // update recordMeta state in app.js
                        this.setRecordState({newRecord: record});
                    }
                }).catch(error => {
                    console.log(error);
                    this.setMessage({
                        message: 'An API error has occurred',
                        messageClass: 'alert alert-danger'
                    });
                    this.setRecordState({
                        newRecord: record,
                    });
                });
            }
        }
        return false
    };

    setMessage = ({message = null, messageClass = ''} = {}) => {
        this.setState({message: message, messageClass: messageClass});
    };

    render() {
        return (
            <div className={'app-main'}>
                <div className={'container'}>
                    <div className={'row'}>
                        <div className={'col-12'}>
                            <Header authMeta={this.state.authMeta}
                                    apiOptions={this.apiOptions}
                                    csrfToken={this.state.csrfToken}
                                    setMessage={this.setMessage}
                                    getSessionStorage={this.getSessionStorage}
                                    setSessionStorage={this.setSessionStorage}
                                    deleteSessionStorage={this.deleteSessionStorage}
                                    setAuthentication={this.setAuthentication}
                            />
                            <Message message={this.state.message}
                                     messageClass={this.state.messageClass}
                            />
                            <DataTable record={this.state.record}
                                       apiOptions={this.apiOptions}
                                       setRecordState={this.setRecordState}
                                       setMessage={this.setMessage}
                                       getRecordsHandler={this.getRecordsHandler}
                                       authMeta={this.state.authMeta}
                            />
                            <Footer footer={process.env.REACT_APP_FOOTER}
                                    copyright={process.env.REACT_APP_COPYRIGHT}
                                    version={process.env.REACT_APP_VERSION}
                            />
                        </div>
                    </div>
                </div>
            </div>
        );
    };
}

export default App;

/* GENERAL NOTES
- state.record should only ever be set using setRecordState.
 */