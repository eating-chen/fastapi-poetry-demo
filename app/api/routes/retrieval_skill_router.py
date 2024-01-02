import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

import app.models.schemas.retrieval_schema as retrieval_schema
from app.db.crud.retrieval_crud import RetrievalDatasetCRUD, RetrievalSkillCRUD
from app.db.events import get_db
from app.error_handler import ChatbotException
from app.services.chatbot_manager import CHATBOT_MANAGER
from app.services.manager.retrieval_manager import RetrievalSkillManager

router = APIRouter()


@router.get(
    "/chatbots/{chatbots_id}/retrieval",
    status_code=status.HTTP_200_OK,
    tags=["Retrieval"],
    summary="查看所有Retrieval Skill",
    response_model=retrieval_schema.RetrievalSkillOutputList,
)
def get_retrieval_skills(chatbots_id: int, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbots_id)
    if not chatbot_service or "Retrieve" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbots_id, chatbot_exist=chatbot_service, skill_name="retrieval"
        )

    retrieval_list = RetrievalSkillCRUD(_db).get_all_retrieval_skill(chatbots_id)
    for retrieval in retrieval_list:
        dataset_id_list = RetrievalSkillCRUD(_db).get_used_retrieval_dataset_id(retrieval.skill_id)
        retrieval.mount_datasets = set([dataset_id for dataset_id in dataset_id_list])
    return {"retrieval_skill_list": retrieval_list}


@router.post(
    "/chatbots/{chatbots_id}/retrieval",
    status_code=status.HTTP_201_CREATED,
    tags=["Retrieval"],
    summary="創建Retrieval Skill",
    response_model=retrieval_schema.RetrievalSkillOutput,
)
def create_retrieval_skills(
    chatbots_id: int, skill_data: retrieval_schema.RetrievalSkillInput, _db: get_db = Depends()
):
    """
    創建Retrieval Skill 參數設定說明
    |Parameter|Description|
    |---------|-----------|
    |skill_name|retrieval skill 命名|
    """
    chatbot_service = CHATBOT_MANAGER.get_service(chatbots_id)
    if not chatbot_service:
        raise ChatbotException(chatbot_id=chatbots_id, chatbot_exist=chatbot_service)

    skill_manager = None
    if chatbot_service is not None and "Retrieve" in chatbot_service.skill_manager:
        skill_manager = chatbot_service.get_manager("Retrieve")
    else:
        skill_manager = RetrievalSkillManager(_db, chatbots_id)
        chatbot_service.add_skill_manager(_db, "Retrieve", skill_manager)
    # create
    skill_data = skill_manager.create_skill(_db, skill_data)
    logging.info(f"Create retrieval skill {skill_data.skill_id} in chatbot {chatbots_id}")
    return skill_data


@router.delete(
    "/chatbots/{chatbots_id}/retrieval/{skill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Retrieval"],
    summary="刪除特定Retrieval Skill",
)
def delete_retrieval_skills(chatbots_id: int, skill_id: int, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbots_id)
    if not chatbot_service or "Retrieve" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbots_id, chatbot_exist=chatbot_service, skill_name="retrieval"
        )

    skill_manager = chatbot_service.get_manager("Retrieve")

    skill_manager.delete_skill(_db, skill_id)
    retrieval_list = RetrievalSkillCRUD(_db).get_all_retrieval_skill(chatbots_id)
    datasets_list = RetrievalDatasetCRUD(_db).get_all_retrieval_datasets(chatbots_id)
    if retrieval_list == [] or datasets_list == []:
        chatbot_service.delete_skill_manager("Retrieve")


@router.get(
    "/chatbots/{chatbots_id}/retrieval/datasets",
    status_code=status.HTTP_200_OK,
    tags=["Retrieval"],
    summary="查看所有Retrieval Datasets",
    response_model=retrieval_schema.RetrievalDatasetOutputList,
)
def get_retrieval_datasets(chatbots_id: int, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbots_id)
    if not chatbot_service or "Retrieve" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbots_id, chatbot_exist=chatbot_service, skill_name="retrieval"
        )

    retrieval_datasets_list = RetrievalDatasetCRUD(_db).get_all_retrieval_datasets(chatbots_id)
    return {"retrieval_dataset_list": retrieval_datasets_list}


@router.post(
    "/chatbots/{chatbots_id}/retrieval/datasets",
    status_code=status.HTTP_201_CREATED,
    tags=["Retrieval"],
    summary="創建Retrieval Dataset",
    response_model=retrieval_schema.RetrievalDatasetOutput,
)
def create_retrieval_dataset(
    chatbots_id: int,
    dataset: retrieval_schema.RetrievalDatasetInput = Depends(
        retrieval_schema.RetrievalDatasetInput.as_form
    ),
    _db: get_db = Depends(),
):
    """
    上傳dataset 參數設定說明
    |Parameter|Description|
    |---------|-----------|
    |dataset_name|資料集命名|
    |segment|True為對文章進行對句，預設為False|
    |file|上傳的檔案|

    上傳檔案 格式說明
    |Attribute|Description|
    |---------|-----------|
    |content|必要，為retrieval搜尋依據|
    |(other)|可自行加入其他attribute|
    """
    chatbot_service = CHATBOT_MANAGER.get_service(chatbots_id)
    if not chatbot_service:
        raise ChatbotException(chatbot_id=chatbots_id, chatbot_exist=chatbot_service)

    skill_manager = None
    if chatbot_service is not None and "Retrieve" in chatbot_service.skill_manager:
        skill_manager = chatbot_service.get_manager("Retrieve")
    else:
        skill_manager = RetrievalSkillManager(_db, chatbots_id)
        chatbot_service.add_skill_manager(_db, "Retrieve", skill_manager)
    dataset = skill_manager.create_dataset(_db, dataset)
    logging.info(f"Create retrieval dataset {dataset.dataset_id} in chatbot {chatbots_id}")
    return dataset


@router.delete(
    "/chatbots/{chatbots_id}/retrieval/datasets/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Retrieval"],
    summary="刪除特定Retrieval Dataset",
)
def delete_retrieval_dataset(chatbots_id: int, dataset_id: int, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbots_id)
    if not chatbot_service or "Retrieve" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbots_id, chatbot_exist=chatbot_service, skill_name="retrieval"
        )
    skill_manager = chatbot_service.get_manager("Retrieve")
    skill_manager.delete_dataset(_db, dataset_id)
    retrieval_list = RetrievalSkillCRUD(_db).get_all_retrieval_skill(chatbots_id)
    datasets_list = RetrievalDatasetCRUD(_db).get_all_retrieval_datasets(chatbots_id)
    if not datasets_list and not retrieval_list:
        chatbot_service.delete_skill_manager("Retrieve")


@router.post(
    "/chatbots/{chatbots_id}/retrieval/{skill_id}/mount",
    status_code=status.HTTP_200_OK,
    tags=["Retrieval"],
    summary="掛載資料集至skill",
    response_model=retrieval_schema.MountOutputlist,
)
def mount_retrieval_dataset_on_skill(
    chatbots_id: int,
    skill_id: int,
    dataset_id_list: retrieval_schema.MountInput,
    _db: get_db = Depends(),
):
    """
    掛載資料集至skill 參數設定說明
    |Parameter|Description|
    |---------|-----------|
    |dataset_id_list|欲掛載的資料庫id list ex.[3,7]|
    """
    chatbot_service = CHATBOT_MANAGER.get_service(chatbots_id)
    if not chatbot_service or "Retrieve" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbots_id, chatbot_exist=chatbot_service, skill_name="retrieval"
        )
    skill_manager = chatbot_service.get_manager("Retrieve")
    dataset = skill_manager.mount_dataset_on_skill(_db, skill_id, dataset_id_list.dataset_id_list)
    if dataset:
        logging.info(f"The valid dataset is {dataset}")
        return {"mount_list": dataset}
    else:
        logging.error(
            f"No valid dataset in the dataset_id_list:{dataset_id_list.dataset_id_list}. The dataset ids does not exist or is not in chatbot {chatbots_id}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"No valid dataset in the dataset_id_list:{dataset_id_list.dataset_id_list}. The dataset ids does not exist or is not in chatbot {chatbots_id}",
        )


@router.post(
    "/chatbots/{chatbots_id}/retrieval/{skill_id}/deploy",
    status_code=status.HTTP_200_OK,
    tags=["Retrieval"],
    summary="部署Retrieval Skill",
)
def deploy(chatbots_id: int, skill_id: int, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbots_id)
    if not chatbot_service or "Retrieve" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbots_id, chatbot_exist=chatbot_service, skill_name="retrieval"
        )
    skill_manager = chatbot_service.get_manager("Retrieve")

    skill_obj = skill_manager.get_skill(skill_id)
    dataset_id_list = skill_manager.get_used_dataset(_db, skill_id)
    if not dataset_id_list:
        logging.error(f"skill_id {skill_id} in chatbot {chatbots_id} does not mount any dataset")
        raise HTTPException(
            status_code=400,
            detail=f"skill_id {skill_id} in chatbot {chatbots_id} does not mount any dataset",
        )
    dataset_obj_list = [
        skill_manager.get_dataset(_db, dataset_id) for dataset_id in dataset_id_list
    ]
    annoy_file_name, deploy_time = skill_obj.retrieval_pipline(dataset_obj_list)
    RetrievalSkillCRUD(_db).set_retrieval_skill_deploy_model_path(
        skill_id, annoy_file_name, deploy_time
    )
    return JSONResponse(
        content={"detail": f"skill_id {skill_id} in chatbot {chatbots_id} deploy success"},
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/chatbots/{chatbots_id}/retrieval/{skill_id}/query",
    status_code=status.HTTP_200_OK,
    tags=["Retrieval"],
    summary="進行Retrieval inference",
    response_model=retrieval_schema.InferenceOutputList,
    response_model_exclude_unset=True,
)
def query(
    chatbots_id: int,
    skill_id: int,
    input_params: retrieval_schema.InferenceInput,
    _db: get_db = Depends(),
):
    """
    進行Retrieval inference 參數設定說明
    |Parameter|Description|
    |---------|-----------|
    |question|搜尋的文字內容'
    |weight|範圍為0~1之間，接近0則傾向embedding比對的結果，接近1則為BM25分數結果，預設值為0.5|
    |threshold|只有分數高於設定的 threshold 的結果才會回傳，預設為0|
    |num_results|回傳結果的筆數，預設為10|
    """

    chatbot_service = CHATBOT_MANAGER.get_service(chatbots_id)
    if not chatbot_service or "Retrieve" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbots_id, chatbot_exist=chatbot_service, skill_name="retrieval"
        )
    skill_manager = chatbot_service.get_manager("Retrieve")
    skill_obj = skill_manager.get_skill(skill_id)

    if not skill_obj.deploy_time:
        logging.error(f"chatbot {chatbots_id} retrieval skill {skill_id} does not deploy yet")
        raise HTTPException(
            status_code=400,
            detail=f"chatbot {chatbots_id} retrieval skill {skill_id} does not deploy yet",
        )

    dataset_id_list = skill_manager.get_used_dataset(_db, skill_id)
    dataset_obj_list = [
        skill_manager.get_dataset(_db, dataset_id) for dataset_id in dataset_id_list
    ]
    return {"result": skill_obj.inference(input_params, dataset_obj_list)}
