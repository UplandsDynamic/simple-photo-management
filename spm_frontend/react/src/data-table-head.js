import './css/data-table.css';
import React from 'react'

const DataTableHead = ({handleColumnOrderChange, record} = {}) => {
    return (
        <tr className={'d-flex text-center'}>
            <th className={'col-6'} scope={'col'}
                onClick={() => console.log('TODO: METHOD TO OPEN LARGE IN A MODAL')}>
                Photo
            </th>
            <th className={'col-2'} scope={'col'}
                onClick={() => handleColumnOrderChange({record, newOrder: 'file_name'})}>
                Filename
            </th>
            <th className={'col-3'} scope={'col'}
                onClick={() => console.log('Nothing to see here ...')}>
                Tags
            </th>
            <th className={'col-1 action-col'} scope={'col'}>
                Action
            </th>
        </tr>
    )
};

export default DataTableHead;