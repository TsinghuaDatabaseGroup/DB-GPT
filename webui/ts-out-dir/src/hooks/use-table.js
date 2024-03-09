import { ref } from 'vue';
import momentMini from 'moment-mini';
import { elConfirm, elMessage } from './use-element';
export const useTable = (searchForm, selectPageReq) => {
    const tableListData = ref([]);
    const totalPage = ref(0);
    const pageNum = ref(1);
    const pageSize = ref(20);
    const tableListReq = (config) => {
        const data = Object.assign({
            pageNum: pageNum.value,
            pageSize: pageSize.value
        }, JSON.parse(JSON.stringify(searchForm)));
        Object.keys(data).forEach((fItem) => {
            if (['', null, undefined, Number.NaN].includes(data[fItem]))
                delete data[fItem];
            if (config.method === 'get') {
                if (Array.isArray(data[fItem]))
                    delete data[fItem];
                if (data[fItem] instanceof Object)
                    delete data[fItem];
            }
        });
        const reqConfig = {
            data,
            ...config
        };
        return axiosReq(reqConfig);
    };
    const dateRangePacking = (timeArr) => {
        if (timeArr && timeArr.length === 2) {
            searchForm.startTime = timeArr[0];
            if (searchForm.endTime) {
                searchForm.endTime = momentMini(timeArr[1]).endOf('day').format('YYYY-MM-DD HH:mm:ss');
            }
        }
        else {
            searchForm.startTime = '';
            searchForm.endTime = '';
        }
    };
    const handleCurrentChange = (val) => {
        pageNum.value = val;
        selectPageReq();
    };
    const handleSizeChange = (val) => {
        pageSize.value = val;
        selectPageReq();
    };
    const resetPageReq = () => {
        pageNum.value = 1;
        selectPageReq();
    };
    const multipleSelection = ref([]);
    const handleSelectionChange = (val) => {
        multipleSelection.value = val;
    };
    const multiDelBtnDill = (reqConfig) => {
        let rowDeleteIdArr = [];
        let deleteNameTitle = '';
        rowDeleteIdArr = multipleSelection.value.map((mItem) => {
            deleteNameTitle = `${deleteNameTitle + mItem.id},`;
            return mItem.id;
        });
        if (rowDeleteIdArr.length === 0) {
            elMessage('表格选项不能为空', 'warning');
            return;
        }
        const stringLength = deleteNameTitle.length - 1;
        elConfirm('删除', `您确定要删除【${deleteNameTitle.slice(0, stringLength)}】吗`).then(() => {
            const data = rowDeleteIdArr;
            axiosReq({
                data,
                method: 'DELETE',
                bfLoading: true,
                ...reqConfig
            }).then(() => {
                elMessage('删除成功');
                resetPageReq();
            });
        });
    };
    const tableDelDill = (row, reqConfig) => {
        elConfirm('确定', `您确定要删除【${row.id}】吗？`).then(() => {
            axiosReq(reqConfig).then(() => {
                resetPageReq();
                elMessage(`【${row.id}】删除成功`);
            });
        });
    };
    return {
        pageNum,
        pageSize,
        totalPage,
        tableListData,
        tableListReq,
        dateRangePacking,
        multipleSelection,
        handleSelectionChange,
        handleCurrentChange,
        handleSizeChange,
        resetPageReq,
        multiDelBtnDill,
        tableDelDill
    };
};
