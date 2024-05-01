'use strict';

import { Modal } from 'flowbite';
import tinybind from 'tinybind';

import './app.css';

function App() {
    let mdlInboxRules, mdlChooseStorage;
    const $mdlInboxRules = document.getElementById('inbox-rules-modal');
    const $mdlChooseStorage = document.getElementById('choose-storage-modal');
    const $ddlSelectStorage = document.getElementById('ddlSelectStorage');
    const $svgChooseFolderLoading = document.getElementById('svgChooseFolderLoading');
    const $btnConfirmGDriveFolder = document.getElementById('btnConfirmGDriveFolder');

    const inputErrorClass = ['bg-red-50', 'border-red-500', 'text-red-900', 'placeholder-red-700', 'dark:text-red-500', 'dark:placeholder-red-500', 'dark:border-red-500'];
    const inputValidClass = ['bg-gray-50', 'border-gray-300', 'text-gray-900', 'dark:bg-gray-700', 'dark:border-gray-600', 'dark:placeholder-gray-400', 'dark:text-white'];

    var objInboxRules = {
        inbox_rules: [],
        destroy: (event, args) => {
            event.preventDefault();

            const thisIndex = args.$index;
            const thisRule = objInboxRules.inbox_rules[thisIndex];

            if(thisRule['id']) {
                // delete rule from db
            } else {
                // just remove locally
                objInboxRules.inbox_rules.splice(thisIndex, 1);
            }
        },
        apply: async (event, args) => {
            event.preventDefault();

            const $thisElem = event.currentTarget;

            const $thisRow = $thisElem.closest('tr.row-inbox-rule');

            const thisIndex = args.$index;
            const thisRule = objInboxRules.inbox_rules[thisIndex];
            const accountId = $mdlInboxRules.dataset.accountId;

            // validate object
            if(!thisRule['email_from']) {
                $thisRow.querySelector('input.input-inbox-rule-email-from').classList.add(...inputErrorClass);
                $thisRow.querySelector('input.input-inbox-rule-email-from').classList.remove(...inputValidClass);
            } else {
                $thisRow.querySelector('input.input-inbox-rule-email-from').classList.remove(...inputErrorClass);
                $thisRow.querySelector('input.input-inbox-rule-email-from').classList.add(...inputValidClass);
            }

            if(!thisRule['attachment_password']) {
                thisRule['attachment_password'] = '';
            }

            thisRule['apply_loading'] = true;
            if(thisRule['id']) {
                // update existing rule
                const reqUrl = '/api/linked_accounts/'+ accountId +'/inbox_rules/' + thisRule['id']
                const response = await fetch(reqUrl, {
                    method: "POST", // or 'PUT'
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(thisRule),
                });
                thisRule['apply_loading'] = false;
                if (response.status === 200) {
                    thisRule['edit_mode'] = false;
                }
            } else {
                // create new rule
                const response = await fetch('/api/linked_accounts/'+ accountId +'/inbox_rules', {
                    method: "POST", // or 'PUT'
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(thisRule),
                });


                thisRule['apply_loading'] = false;

                if (response.status === 201) {
                    const result = await response.json();
                    thisRule['id'] = result['id'];
                    thisRule['edit_mode'] = false;
                }
            }


        },
        edit: (event, args) => {
            const thisIndex = args.$index;
            const thisRule = objInboxRules.inbox_rules[thisIndex];

            thisRule['edit_mode'] = true;
        },
        chooseStorage: (event, args) => {
            event.preventDefault();

            const thisIndex = args.$index;
            const thisRule = objInboxRules.inbox_rules[thisIndex];

            $mdlChooseStorage.dataset.ruleId = thisRule.id;
            $mdlChooseStorage.dataset.ruleIndex = thisIndex;

            mdlChooseStorage.show();
        }
    };

    const fnLoadInboxRules = async (accountId) => {
        const response = await fetch('/api/linked_accounts/'+ accountId +'/inbox_rules');
        const data = await response.json();
        objInboxRules.inbox_rules = data.inbox_rules;
    };

    const fnGetLinkedAccount = async(accountId) => {
        const response = await fetch('/api/linked_accounts/'+ accountId);
        if(response.ok) {
            const data = await response.json();
            return data;
        } else {
            return {};
        }

    }

    const initModals = () => {
        mdlInboxRules = new Modal($mdlInboxRules, {
            closable: true,
            onHide: () => {
                $mdlInboxRules.dataset.accountId = '';
            },
            onShow: () => {
                fnLoadInboxRules($mdlInboxRules.dataset.accountId);
            },
        });

        mdlChooseStorage = new Modal($mdlChooseStorage, {
            closable: true,
            onHide: () => {
                $mdlChooseStorage.dataset.ruleId = '';
                $mdlChooseStorage.dataset.ruleIndex = '';
                $ddlSelectStorage.value = 'NaN';
            },
        });
    };

    const showGDrivePicker = (accessToken, pickerCallback) => {
        const DisplayView = new google.picker.DocsView(google.picker.ViewId.FOLDERS).setSelectFolderEnabled(true);

        const picker = new google.picker.PickerBuilder()
            .addView(DisplayView)
            .setOAuthToken(accessToken)
            .setCallback(pickerCallback)
            .build();
        picker.setVisible(true);
    };

    const fnAttachEventListener = () => {
        document.getElementById('btnShowDrivePicker').addEventListener('click', () => {
            // A simple callback implementation.
            function pickerCallback(data) {
                let url = 'nothing';

            }
        });

        document.getElementById('btnCloseIBRuleModal').addEventListener('click', () => {
            mdlInboxRules.hide();
        });

        document.getElementById('btnCloseChooseStorageModal').addEventListener('click', () => {
            mdlChooseStorage.hide();
        });

        document.getElementById('btnAddNewRule').addEventListener('click', () => {
            objInboxRules.inbox_rules.push({
                edit_mode: true
            });
        });

        [...document.getElementsByClassName('event-lnk-inbox-rules')].forEach(function(elem) {
            elem.addEventListener('click', function(e){
                e.preventDefault();

                $mdlInboxRules.dataset.accountId = this.dataset.accountId;
                mdlInboxRules.show();
            });
        });

        document.getElementById('lnkChooseFolder').addEventListener('click', async (e) => {
            e.preventDefault();

            const selectedAccountId = $ddlSelectStorage.value;
            if(selectedAccountId === 'NaN')
                return;

            $svgChooseFolderLoading.classList.remove('collapse');

            const objAccount = await fnGetLinkedAccount(selectedAccountId);
            $svgChooseFolderLoading.classList.add('collapse');

            showGDrivePicker(objAccount.access_token, (data) => {
                if (data[google.picker.Response.ACTION] == google.picker.Action.PICKED) {
                    const selectedDoc = data.docs[0];

                    if (selectedDoc['type'] !== 'folder') {
                        alert('Please select a folder');
                        return;
                    }

                    $btnConfirmGDriveFolder.dataset.selectedFolderName = selectedDoc['name'];
                    $btnConfirmGDriveFolder.dataset.selectedFolderId = selectedDoc['id'];

                    document.getElementById('spFolderName').innerText = selectedDoc['name'];
                }
            });
        });

        $btnConfirmGDriveFolder.addEventListener('click', (e) => {
            e.preventDefault();

            const thisFolderName = $btnConfirmGDriveFolder.dataset.selectedFolderName;
            const thisFolderId =  $btnConfirmGDriveFolder.dataset.selectedFolderId;

            const thisIndex = $mdlChooseStorage.dataset.ruleIndex;

            const thisRule = objInboxRules.inbox_rules[thisIndex];

            thisRule['destination_folder_id'] = thisFolderId;
            thisRule['destination_folder_name'] = thisFolderName;
            thisRule['destination_account_id'] = $ddlSelectStorage.value;

            mdlChooseStorage.hide();
        });

        [...document.getElementsByClassName('event-refresh-account-token')].forEach(function(elem) {
            elem.addEventListener('click', async function(e){
                e.preventDefault();

                const accountId = this.dataset.accountId;
                const response = await fetch('/api/linked_accounts/'+ accountId +'/refresh_token', {
                    method: "POST", // or 'PUT'
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({}),
                });
            });
        });

    };

    this.init = () => {
        fnAttachEventListener();
        initModals();

        tinybind.bind(document.getElementById('tblInboxRules'), objInboxRules);
    }
}

(() => {
    const app = new App();
    app.init(PAGE_NAME);
})();
