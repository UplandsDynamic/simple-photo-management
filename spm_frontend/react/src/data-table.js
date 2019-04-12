import React from 'react';
import './css/data-table.css';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.js'
import moment from 'moment'
import 'moment/locale/en-gb.js'
import 'moment-timezone'
import DataTableNav from "./data-table-nav";
import DataTableData from "./data-table-data";
import DataTableHead from "./data-table-head";

const DataTable = ({
                       record = {}, apiOptions = {}, setMessage, getRecordsHandler, authMeta = {}, setRecordState,
                   } = {}) => {

    const _formatUTCDateTime = ({dateTime = null} = {}) => {
        // takes datetime in UTC, formats and returns datetime in user's browser reported timezone
        return dateTime ? `${moment.utc(dateTime).local()
                .format('DD/MM/YYYY HH:mm:ss')} ${moment.tz(moment.tz.guess()).zoneAbbr()}`
            : null;
    };

    const _handleColumnOrderChange = ({record = {}, newOrder = {}} = {}) => {
        let {pageOrderDir, pageOrderBy} = record.meta;
        // set page order direction
        pageOrderDir = (!pageOrderBy || pageOrderDir === '-') ? '' : '-';  // *see note 1
        Object.assign(record.meta, {pageOrderBy: newOrder, pageOrderDir, page: 1}); // maybe page:1 ?
        getRecordsHandler({record})
    };

    const _handleSearch = ({record = {}, term = null} = {}) => {
        if (record) {
            Object.assign(record.meta, {
                pageOrderBy: 'desc', page: 1,
                search: _validateDesc(term)
            });
            /* set new record state early, even though record again when API returns,
            to ensure search string change keeps pace with user typing speed
             */
            setRecordState({newRecord: record});
            // get the matching records from the API
            getRecordsHandler({record});
        }
    };

    const _validateDesc = (value) => {
        return (/^[a-zA-Z\d.\- ]*$/.test(value)) ? value : record.meta.search
    };

    return (
        <div className={'data-table'}>
            <DataTableNav
                record={record}
                handleGetRecords={getRecordsHandler}
                handleSearch={_handleSearch}
                authMeta={authMeta}
            />
            <div className={'container'}>
                <div className={'row'}>
                    <div className={'col-sm table-responsive table-sm'}>
                        <table className="table table-bordered table-dark table-hover">
                            <caption>{process.env.REACT_APP_SHORT_ORG_NAME} Photo Data
                                {record.meta.datetime_of_request ?
                                    `[Request returned:
                                        ${_formatUTCDateTime({
                                        dateTime: record.meta.datetime_of_request
                                    })}]` : ''}
                            </caption>
                            <thead>
                            <DataTableHead
                                record={record}
                                handleColumnOrderChange={_handleColumnOrderChange}
                            />
                            </thead>
                            <tbody>
                            <DataTableData
                                record={record}
                                formatUTCDateTime={_formatUTCDateTime}
                                authMeta={authMeta}
                            />
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

        </div>
    )
};

export default DataTable;
