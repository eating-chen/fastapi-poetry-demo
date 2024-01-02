import logging
import os

import mlflow
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.db.events import get_db
from app.error_handler import ChatbotException
from app.models.schemas.modelmanager_schema import (
    AllModelInfo,
    ImportInput,
    ImportOutput,
    ModelInfo,
    TrainInput,
    TrainOutput,
)
from app.services.chatbot_manager import CHATBOT_MANAGER
from app.services.manager.modelmanager_manager import ModelSkillManager

router = APIRouter()


@router.post(
    "/{chatbot_pk}/models",
    response_model=TrainOutput,
    status_code=status.HTTP_201_CREATED,
    tags=["ModelManager"],
    summary="訓練模型",
)
def create_and_train_model(train_detail: TrainInput, chatbot_pk: int, _db: get_db = Depends()):
    """
    request 說明

    |參數|說明|Optional|
    |---|---|---|
    |task|訓練任務的類型，目前Slu僅提Slu-intent、Slu-slot、Slu-both等三種|false|
    |skill|目前訓練的模型是屬於哪個Skill|false|
    |skill_id|目前訓練模型是屬於哪個Skill底下的第幾個Skill|false|
    |training_args|訓練模型的基本參數，如未指定則會使用預設參數進行訓練，請參考範例輸入|true|
    |early_stop|訓練模型是否要提前終止，如果指定則會使用預設值，請參考範例輸入|true|
    |train_data|訓練資料，格式請依照任務進行更改，請參考範例輸入|false|
    |eval_data|評估資料，格式與train_data相同，如未輸入則會從訓練資料中自動切分|true|

    training_args 和 early_stop 設定說明

    |參數|說明|
    |---|---|
    |epoch|訓練的回合數，越高則需要花費的時間可能越長，但也可以提高模型的表現，給定範圍[1,30]，預設值為2|
    |train_batch_size|訓練模型的batch資料量，越高需要訓練的時間也會越長，計算的硬體需求也會越大，給定範圍[1,128]，預設為16|
    |learning_rate|模型的學習率，越低可以提高模型的表現，但訓練時間也會越久，給定範圍[1e-5,1e-3]，預設為1e-5|
    |weight_decay|值越大容易導致underfitting，給定範圍[1,1e-5], 預設為0.01|
    """
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if not chatbot_service:
        raise ChatbotException(chatbot_id=chatbot_pk, chatbot_exist=chatbot_service)
    skill_manager = None
    if "ModelManager" in chatbot_service.skill_manager:
        skill_manager = chatbot_service.get_manager("ModelManager")
    else:
        skill_manager = ModelSkillManager(_db, chatbot_pk)
        chatbot_service.add_skill_manager(_db, "ModelManager", skill_manager)
    # add data to DB
    model_data = skill_manager.create_skill(_db, train_detail)
    # train model
    skill_obj = skill_manager.get_skill(model_data.id)
    save_path = None
    if "SLU" in train_detail.task:
        save_path = skill_obj.train_slu(train_detail.train_data, train_detail.eval_data)
    logging.info(f"Create model {model_data.id} in chatbot {chatbot_pk}")
    mlflow_result = (
        os.getenv("MLFLOW_TRACKING_URI")
        if os.getenv("MLFLOW_TRACKING_URI")
        else mlflow.get_tracking_uri()
    )
    return {
        "skill": model_data.skill,
        "skill_id": model_data.skill_id,
        "model_id": model_data.id,
        "task": model_data.task,
        "mlflow_result": mlflow_result,
        "saved_path": save_path,
    }


@router.delete(
    "/{chatbot_pk}/models/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["ModelManager"],
    summary="刪除模型",
)
def delete_model(model_id: int, chatbot_pk: int, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if not chatbot_service or "ModelManager" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbot_pk, chatbot_exist=chatbot_service, skill_name="ModelManager"
        )
    skill_manager = chatbot_service.get_manager("ModelManager")
    skill_manager.delete_skill(_db, model_id)
    logging.info(f"Delete model {model_id} in chatbot {chatbot_pk}")
    if skill_manager.skill_services is None or not bool(skill_manager.skill_services):
        chatbot_service.delete_skill_manager(_db, "ModelManager")


@router.get(
    "/{chatbot_pk}/models",
    response_model=AllModelInfo,
    status_code=status.HTTP_200_OK,
    tags=["ModelManager"],
    summary="條列所有模型",
)
def get_all_models(chatbot_pk: int, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if not chatbot_service or "ModelManager" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbot_pk, chatbot_exist=chatbot_service, skill_name="ModelManager"
        )
    skill_manager = chatbot_service.get_manager("ModelManager")
    model_list = skill_manager.get_all_models(_db)
    return {"all_model_info": model_list}


@router.get(
    "/{chatbot_pk}/models/{model_id}",
    response_model=ModelInfo,
    status_code=status.HTTP_200_OK,
    tags=["ModelManager"],
    summary="條列特定模型",
)
def get_certain_model(chatbot_pk: int, model_id: int, _db: get_db = Depends()):
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if not chatbot_service or "ModelManager" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbot_pk, chatbot_exist=chatbot_service, skill_name="ModelManager"
        )
    skill_manager = chatbot_service.get_manager("ModelManager")
    model_data = skill_manager.get_certain_model(_db, model_id)
    if not model_data:
        raise HTTPException(status_code=404, detail=f"model {model_id} is not found")
    return model_data


@router.get(
    "/{chatbot_pk}/models/{model_id}/export",
    status_code=status.HTTP_200_OK,
    tags=["ModelManager"],
    summary="匯出模型",
)
def export_model(chatbot_pk: int, model_id: int, _db: get_db = Depends()):
    """
    將指定model_id的模型相關檔案匯出為壓縮檔，並回傳給使用者
    """
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if not chatbot_service or "ModelManager" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbot_pk, chatbot_exist=chatbot_service, skill_name="ModelManager"
        )
    skill_manager = chatbot_service.get_manager("ModelManager")
    skill_obj = skill_manager.get_skill(model_id)
    zip_model = skill_obj.export_mlflow_model(model_id)
    logging.info(f"Export model {model_id} from chatbot {chatbot_pk}. Check file at '{zip_model}'")
    return FileResponse(zip_model, filename=f"model_{model_id}.zip")


@router.post(
    "/{chatbot_pk}/models/import",
    status_code=status.HTTP_201_CREATED,
    tags=["ModelManager"],
    summary="匯入模型",
    response_model=ImportOutput,
)
def import_model(
    chatbot_pk: int,
    import_input: ImportInput = Depends(ImportInput.as_form),
    _db: get_db = Depends(),
):
    """
    上傳模型相關壓縮檔至mlflow

    - **chatbot_pk**: 模型要匯入哪個chatbot底下的mlflow實驗中

    - **skill_id**: 模型所對應的skill的id為何

    - **uploadfile**: 要匯入的壓縮檔路徑 e.g. uploadfile = @"path/to/model.zip"

    """
    skill_id = import_input.skill_id
    uploadfile = import_input.uploadfile
    chatbot_service = CHATBOT_MANAGER.get_service(chatbot_pk)
    if not chatbot_service or "ModelManager" not in chatbot_service.skill_manager:
        raise ChatbotException(
            chatbot_id=chatbot_pk, chatbot_exist=chatbot_service, skill_name="ModelManager"
        )
    if "ModelManager" in chatbot_service.skill_manager:
        skill_manager = chatbot_service.get_manager("ModelManager")
    else:
        skill_manager = ModelSkillManager(_db, chatbot_pk)
        chatbot_service.add_skill_manager(_db, "ModelManager", skill_manager)

    (
        model_metric,
        model_params,
        model_tags,
        original_request,
        temp_dir,
    ) = skill_manager.extract_file_and_get_info(uploadfile)
    import_input = skill_manager.make_traininput(original_request, skill_id)
    model_data = skill_manager.create_skill(_db, import_input)
    skill_obj = skill_manager.get_skill(model_data.id)
    upload_experiment, upload_run = skill_obj.upload_model_to_mlflow(
        model_params, model_tags, model_metric, temp_dir
    )
    logging.info(f"Create model {model_data.id} in chatbot {chatbot_pk}")
    mlflow_result = (
        os.getenv("MLFLOW_TRACKING_URI")
        if os.getenv("MLFLOW_TRACKING_URI")
        else mlflow.get_tracking_uri()
    )
    return {
        "tracking_uri": mlflow_result,
        "experiemnt_name": f"chatbot-{upload_experiment}",
        "run_name": upload_run,
    }
