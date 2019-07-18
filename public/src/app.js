/*version*/
import APP_VERSION from './version'
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
/* debug */
//import './debug';
/* font awesome icons */
import { library } from '@fortawesome/fontawesome-svg-core'
import {
    faSyncAlt, faEllipsisH, faPlus, faPlusSquare, faMinus, faMinusSquare,
    faTrashAlt, faEdit, faRobot, faTags, faBroom, faUndo, faRedo
} from '@fortawesome/free-solid-svg-icons'

library.add(faSyncAlt, faEllipsisH, faPlus, faTrashAlt, faEdit, faPlusSquare, 
    faMinus, faMinusSquare, faRobot, faTags, faBroom, faUndo, faRedo);

axios.defaults.withCredentials = true;

/* App root */
class App extends React.Component {

    constructor(props) {
        super(props); // makes 'this' refer to component (i.e. like python self)
        this.statusMessages = {
            retag: 'Processing of new photos & resync of existing photo tags in progress!',
            scan: 'Processing of newly added photos in progress!',
            clean_db: 'Database cleaning in progress!'
        }
        this.apiOptions = {
            /* used to define available API options in the api-request component */
            GET_PHOTOS: { requestType: 'get_photos', method: 'GET', desc: 'request to get photo data' },
            PROCESS_PHOTOS: { requestType: 'process_photos', method: 'GET', desc: 'request to begin photo re-taggig operation' },
            UPDATE_PHOTOS: { requestType: 'update_photos', method: 'PATCH', desc: 'request to update the photo, e.g. add tags, mutations' },
            // PATCH_PHOTOS: {requestType: 'patch_photos', method: 'PATCH', desc: 'PATCH request to update photo data'},
            // ADD_PHOTOS: {requestType: 'add_add_photos', method: 'POST', desc: 'POST request to add photo data'},
            // DELETE_PHOTOS: {
            //     requestType: 'delete_photos',
            //     method: 'DELETE',
            //     desc: 'DELETE request to delete photos'
            // },
            POST_AUTH: { requestType: 'post_auth', method: 'POST', desc: 'POST request to for authorization' },
            POST_LOGOUT: { requestType: 'post_logout', method: 'POST', desc: 'POST request to for logout of server' },
            PATCH_CHANGE_PW: { requestType: 'patch_change_pw', method: 'PATCH', desc: 'PATCH request to for changing password' },
        };
        this.initialState = {
            record: {
                meta: {
                    page: 1,
                    limit: process.env.REACT_APP_ROWS_PER_TABLE,
                    pagerMainSize: process.env.REACT_APP_PAGER_MAIN_SIZE,
                    pagerEndSize: process.env.REACT_APP_PAGER_END_SIZE,
                    pageOrderBy: 'file_name',
                    pageOrderDir: '',
                    previous: null,
                    next: null,
                    cacheControl: 'no-cache',  // no caching by default, so always returns fresh data
                    search: '',
                },
                data: {
                    results: []                }
            },
            authMeta: {
                authenticated: false,
                userIsAdmin: false,
            },
            greeting: process.env.REACT_APP_GREETING,
            csrfToken: null,
            message: {message: '', messageClass: ''}
        };
        this.state = JSON.parse(JSON.stringify(this.initialState));
        // bind methods to 'this' to enable to be passed as props
        this.setMessage = this.setMessage.bind(this);
        this.getSessionStorage = this.getSessionStorage.bind(this);
        this.setSessionStorage = this.setSessionStorage.bind(this);
        this.deleteSessionStorage = this.deleteSessionStorage.bind(this);
        this.setAuthentication = this.setAuthentication.bind(this);
        this.handleProcessPhotos = this.handleProcessPhotos.bind(this);
        this.getRecordsHandler = this.getRecordsHandler.bind(this);
        this.handleUpdate = this.handleUpdate.bind(this);
    }

    componentDidMount() {
        this.setState({ csrfToken: this.getCSRFToken() });
        // kick off: attempt to authenticate (new authentication also requests stock data)
        this.setAuthentication();
    }

    componentDidUpdate(prevProps, prevState, snapshot) {
    }

    getCSRFToken() {
        return Cookies.get('csrftoken')
    }

    setSessionStorage({ key, value }) {
        sessionStorage.setItem(key, value);
    }

    getSessionStorage(key) {
        //return JSON.parse(localStorage.getItem(key));
        return sessionStorage.getItem(key);
    }

    deleteSessionStorage(keys = []) {
        if (keys.length > 0) {
            keys.forEach((k) => {
                sessionStorage.removeItem(k)
            });
        }
        return true;
    }

    setAuthentication() {
        let authenticated = !!this.getSessionStorage('token');
        let clonedAuthMeta = JSON.parse(JSON.stringify(this.state.authMeta));
        clonedAuthMeta.authenticated = authenticated;
        // set authentication state and fetch new records when done (in a callback)
        this.setState({ authMeta: { ...clonedAuthMeta } }, this.getRecordsHandler);
    }

    setAuthorized({ role = 'admin', state = false } = {}) {
        // called after each api response
        let clonedAuthMeta = JSON.parse(JSON.stringify(this.state.authMeta));
        if (role === 'admin') {
            if (state !== this.state.authMeta.userIsAdmin) {
                clonedAuthMeta.userIsAdmin = state;
                this.setState({ authMeta: { ...clonedAuthMeta } });
            }
        }
    }

    _setRecordState({ newRecord } = {}) {
        /*
        method to update state for record being retrieved (GET request)
         */
        let { page } = newRecord.meta;
        if (newRecord) {
            // ensure page never < 1
            let updatedPage = page < 1 ? 1 : page;
            Object.assign(newRecord.meta, { page: updatedPage });
            // set user admin status to what was returned from api in record data
            const admin = newRecord.data.results.length && 
                newRecord.data.results[0].hasOwnProperty('user_is_admin') ? newRecord.data.results[0].user_is_admin : false;
            if (admin !== this.state.authMeta.userIsAdmin) {
                this.setAuthorized({ role: 'admin', state: admin })
            }
            this.setState({ record: newRecord });
        }
    }

    getRecordsHandler({ record = this.state.record, url = null, notifyResponse = true } = {}) {
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
                        // set new state
                        let recordCopy = JSON.parse(JSON.stringify(this.state.record));
                        Object.assign(recordCopy.data, { ...response.data });
                        Object.assign(recordCopy.meta, { ...record.meta });
                        this._setRecordState({ newRecord: recordCopy });
                    }
                }).catch(error => {
                    console.log(error);
                    this.setMessage({
                        message: 'An API error has occurred',
                        messageClass: 'alert alert-danger'
                    });
                    this._setRecordState({
                        newRecord: record,
                    });
                });
            }
        }
        return false;
    }

    handleProcessPhotos({ record = this.state.record, retag = false, scan = false,
        clean_db = false, notifyResponse = true } = {}) {
        if (this.state.authMeta.authenticated) {
            const apiRequest = processRequest({
                queryFlags: { retag, scan, clean_db },
                apiMode: this.apiOptions.PROCESS_PHOTOS
            });
            if (apiRequest) {
                apiRequest.then((response) => {
                    if (response) {
                        if (notifyResponse) {
                            this.setMessage({
                                message:
                                    retag ? this.statusMessages.retag : scan ?
                                        this.statusMessages.scan : clean_db ? this.statusMessages.clean_db : '',
                                messageClass: 'alert alert-success'
                            });
                        }
                    }
                }).catch(error => {
                    console.log(error);
                    this.setMessage({
                        message: 'An API error has occurred. Photo processing initiation failed!',
                        messageClass: 'alert alert-danger'
                    });
                });
            }
        }
        return false;
    }

    handleUpdate({ record = this.state.record, updateParams,
        recordItem, updateMode, tags = null, notifyResponse = true } = {}) {
        if (this.state.authMeta.authenticated) {
            const apiRequest = processRequest({
                queryFlags: {},
                requestData: {
                    id: recordItem.id,
                    tags: tags ? tags.split('/') : [],
                    update_mode: updateMode,
                    update_params: updateParams,
                },
                apiMode: this.apiOptions.UPDATE_PHOTOS
            });
            if (apiRequest) {
                apiRequest.then((response) => {
                    if (response) {
                        let recordCopy = JSON.parse(JSON.stringify(this.state.record));
                        recordCopy.data.results.forEach((r, idx) => {
                            if (r.id === response.data.id) {
                                Object.assign(recordCopy.data.results[idx], response.data);
                            }
                        });
                        this._setRecordState({ newRecord: recordCopy })
                        if (notifyResponse) {
                            this.setMessage({
                                message: 'Updating tags succeeded!',
                                messageClass: 'alert alert-success'
                            });
                        }
                    }
                }).catch(error => {
                    console.log(error);
                    this.setMessage({
                        message: 'An API error has occurred. Updating tags failed!',
                        messageClass: 'alert alert-danger'
                    });
                });
            }
        }
        return false;
    }

    setMessage({ message = null, messageClass = '' } = {}) {
        this.setState({'message': Object.assign(this.state.message, {message, messageClass})})
    }

    DataTableWrapper() {
        return (
            <DataTable record={this.state.record}
                apiOptions={this.apiOptions}
                setMessage={this.setMessage}
                getRecordsHandler={this.getRecordsHandler}
                handleProcessPhotos={this.handleProcessPhotos}
                authMeta={this.state.authMeta}
                handleUpdate={this.handleUpdate} />
        )
    }
       
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
                            <Message message={this.state.message.message}
                                messageClass={this.state.message.messageClass}
                            />
                            { this.state.authMeta.authenticated ? this.DataTableWrapper() : null}
                            <Footer footer={process.env.REACT_APP_FOOTER}
                                copyright={process.env.REACT_APP_COPYRIGHT}
                                version={APP_VERSION}
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