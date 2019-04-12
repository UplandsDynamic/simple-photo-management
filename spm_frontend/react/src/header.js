import filmLogo from './img/film_icon.png'
import './css/header.css';
import AppNameTitle from './app-name-title'
import LoginForm from './loginform'
import React from 'react'
//import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";

const Header = ({
                    authMeta = {}, apiOptions = null, csrfToken = null, setMessage, getSessionStorage, setSessionStorage,
                    deleteSessionStorage, setAuthentication
                } = {}) => {
    return (
        <React.Fragment>
            <div className={'container header'}>
                <div className={'row'}>
                    <div className={'col-4'}><img className={'logo float-left'} src={filmLogo}
                                                  alt={'Film logo'}/><AppNameTitle/></div>
                    <div className={'col-8'}><LoginForm authMeta={authMeta}
                                                        apiOptions={apiOptions}
                                                        csrfToken={csrfToken}
                                                        setMessage={setMessage}
                                                        getSessionStorage={getSessionStorage}
                                                        setSessionStorage={setSessionStorage}
                                                        deleteSessionStorage={deleteSessionStorage}
                                                        setAuthentication={setAuthentication}
                    /></div>
                </div>
            </div>
        </React.Fragment>
    );
};

export default Header;