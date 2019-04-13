import './css/data-table.css';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import Paginate from './paginate.js';
import React from 'react'

const DataTableNav = ({
                          record = null, handleGetRecords, handleRetagPhotos, handleSearch, authMeta = null
                      } = {}) => {
    const {userIsAdmin} = authMeta;

    if (record) {
        return (
            <React.Fragment>
                <div className={'container'}>
                    <div className={'row nav-row'}>
                        <div className={'col-12'}>
                            <div className={'btn-group float-right'}>
                                <nav className="nav-pagination float-right" aria-label="Table data pages">
                                    <Paginate record={record}
                                              handleGetRecords={handleGetRecords}
                                    />
                                </nav>
                            </div>
                        </div>
                    </div>
                    <div className={'row nav-row'}>
                        <div className={`${userIsAdmin ? 'col-4' : 'col-2'}`}>
                            <div className={'btn-group'}>
                                <button onClick={() => {
                                    Object.assign(record.meta, {page: 1});
                                    handleGetRecords({record})
                                }} className={'btn btn-md btn-warning mr-1 '}>
                                    <FontAwesomeIcon icon={"sync-alt"}/></button>
                                <button onClick={() => {
                                    handleRetagPhotos()
                                }} className={'btn btn-md btn-warning mr-1 '}>
                                    <FontAwesomeIcon icon={"robot"}/></button>
                            </div>
                        </div>
                        <div className={`${userIsAdmin ? 'col-8' : 'col-10'}`}>
                            <nav className={'search-navigation w-100 d-block ml-1'}>
                                <input value={record.meta.search} placeholder={'Search'}
                                       name={'search'} className={'form-control search'}
                                       onChange={(e) =>
                                           handleSearch({record, term: e.target.value})
                                       }/>
                            </nav>
                        </div>
                    </div>
                </div>
            </React.Fragment>
        )
    }
    return null;
};

export default DataTableNav;