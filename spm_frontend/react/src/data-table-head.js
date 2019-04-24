import './css/data-table.css';
import React from 'react'

const DataTableHead = (props) => {
    // const { handleColumnOrderChange, record } = props;  # uncomment if want to click headers to reorder
    return (
        <tr className={'d-flex text-center'}>
            <th className={'col-4'} scope={'col'}>
                Photo
            </th>
            <th className={'col-4'} scope={'col'}>
                Tags
            </th>
            <th className={'col-4 action-col'} scope={'col'}>
                Action
            </th>
        </tr>
    )
};

export default DataTableHead;