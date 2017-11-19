

$(function(){

    $(".signup-form input").on("focus",function(){

        $(this).parent().addClass("border");

    });

    $(".signup-form input").on("blur",function(){

        $(this).parent().removeClass("border");

    })

    //注册方式切换

    $(".signup-select").on("click",function(){

        var _text=$(this).text();

        var $_input=$(this).prev();

        $_input.val('');


        if(_text=="邮箱注册"){

            $(".signup-tel").fadeOut(180);

            $(".signup-email").fadeIn(200);

            $_input.attr("placeholder","邮箱");

            $_input.attr("onblur","verify.verifyEmail(this)");

            $(this).parents(".form-group").find(".error-notic").text("邮箱格式不正确")

        }

    });

    //步骤切换

    var _boxCon=$(".box-con");
    // 已有账号登陆转登陆页面
    $(".move-login").on("click",function(){

        $(_boxCon).css({

            'marginLeft':0

        })

    });
    // 还未注册，转注册页面
    $(".move-signup").on("click",function(){

        $(_boxCon).css({

            'marginLeft':-320

        })

    });
    // 转重置密码页面
    $(".move-reset").on("click",function(){

        $(_boxCon).css({

            'marginLeft':-640

        })

    });

});



//表单验证

function showNotic(_this){

    $(_this).parents(".form-group").find(".error-notic").fadeIn(100);
    // 输入错误禁止下一行输入
    // $(_this).focus();

}//错误提示显示

function hideNotic(_this){

    $(_this).parents(".form-group").find(".error-notic").fadeOut(100);

}//错误提示隐藏

var verify={

    verifyEmail:function(_this){

        var validateReg = /^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$/;

        var _value=$(_this).val();

        if(!validateReg.test(_value)){

            showNotic(_this)

        }else{

            hideNotic(_this)

        }

    },//验证邮箱

    // PasswordLenght:function(_this){
    //
    //     var _length=$(_this).val().length;
    //
    //     if(_length<8){
    //
    //         showNotic(_this)
    //
    //     }else{
    //
    //         hideNotic(_this)
    //
    //     }
    //
    // },//验证设置密码长度

    PasswordLenght:function(_this){

        var strength = /^.*(?=.{8,20})(?=.*\d)(?=.*[A-Z])(?=.*[a-z])(?=.*[\.!@#$%^&*?_]).*$/;

        var space = /(^\s+)|(\s+$)/g;

        var _value=$(_this).val();

        if( strength.test(_value) && !space.test(_value) ){

            hideNotic(_this)

        }else{

            showNotic(_this)

        }

    },//验证设置密码强度

    PasswordEqual:function(_this){

        if($('#equal1 input').val() != $('#equal2 input').val()){
            showNotic(_this)
        }else{
            hideNotic(_this)
        }
    },//再次输入密码

    VerifyCount:function(_this){

        var _count="123456";

        var _value=$(_this).val();

        console.log(_value)

        if(_value!=_count){

            showNotic(_this)

        }else{

            hideNotic(_this)

        }

    }//验证验证码

}