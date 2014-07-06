# coding: utf8
'''
Created on 2013/05/09

@author: n_shimada
'''

import cv2
import cv2.cv as cv
import numpy as np
from scipy.ndimage import filters 
import imtools
import math
from copy import deepcopy

# ヒストグラムのビン数
N_BIN = 9
# 何度ずつに分けて投票するか（分解能）
THETA = 180 / N_BIN
#// セルの大きさ（ピクセル数）
CELL_SIZE = 40
#// ブロックの大きさ（セル数）奇数
BLOCK_SIZE = 3
#// ブロックの大きさの半分（ピクセル数）
R = math.ceil(CELL_SIZE*BLOCK_SIZE*0.5)
R2 = CELL_SIZE*BLOCK_SIZE

MAX_WEAK_CLASSIFIER = 500
BIN = 64        
POS = 1
NEG = 0

# hog.hの内容
"""
CELL = 3 #//セルのサイズ(pixel)
BLOCK = 2 #//ブロックのサイズ(セル)
WIDTH = 18 #//パッチの縦幅(pixel)
HEIGHT = 36 #//パッチの横幅(pixel)
ORIENTATION = 9 #//勾配方向
PI = 3.14
LN_E = 1.0
"""

class create_hog_image(object):
    # ここからmain
    def main(self,im):
        y_block_n = int((im.shape[0] - R)/CELL_SIZE); x_block_n = int((im.shape[1] - R)/CELL_SIZE) 
        
        point = [(R+i*CELL_SIZE,R+j*CELL_SIZE) for i in xrange(y_block_n) for j in xrange(x_block_n)]
        integrals = self.calculate_integral_HOG(im);
        #// ある点(x, y)のHOG特徴量を求めるには
        #// Mat hist = getHOG(Point(x, y), integrals);
        #// とする。histはSize(81, 1) CV_32FのMat
        sample = [self.get_HOG(pt, integrals) for pt in point]
        print sample
        """ 
        # // 表示
        imshow("out", integrals);
        waitKey(0);
         
        return 0;
        """
        
    # 積分画像生成
    def calculate_integral_HOG(self, image):
        # X, Y方向に微分
        xsobel = np.zeros(image.shape)
        filters.sobel(image,1,xsobel) # 1はaxis=1のこと = x方向
        
        ysobel = np.zeros(image.shape)
        filters.sobel(image,0,ysobel) # 1はaxis=0のこと = y方向
        
        # 角度別の画像を生成しておく
        bins = np.zeros((N_BIN, image.shape[0], image.shape[1]))
         
        # X, Y微分画像を勾配方向と強度に変換
        Imag, Iang = cv2.cartToPolar(xsobel, ysobel, None, None, True) # outputs are magnitude, angle
        # 勾配方向を[0, 180)にする(181～360は0～180に統合する。x軸をまたいだ方向は考えない)
        Iang = (Iang>180)*(Iang-180) + (Iang<=180)*Iang 
        Iang[Iang==360] = 0; Iang[Iang==180] = 0 
        # 勾配方向を[0, 1, ..., 8]にする準備（まだfloat）
        Iang /= THETA
        # 勾配方向を強度で重みをつけて、角度別に投票する
        ind = 0

        for ind in xrange(N_BIN):
            bins[ind] += (np.int8(Iang) == ind)*Imag
        
        # 角度別に積分画像生成
        """ ！ここの計算があやしい！ """
        integrals = np.array([cv2.integral(bins[i]) for i in xrange(N_BIN)])
        
        return integrals
    
    
    #// ある矩形領域の勾配ヒストグラムを求める
    #// ここでいう矩形はHOG特徴量のセルに該当
    def calculate_HOG_InCell(self, hog_cell, roi, integrals):
        x0 = roi[1]; y0 = roi[0] 
        x1 = x0 + roi[3]; y1 = y0 + roi[2]
        for i in xrange(N_BIN):
            a = integrals[i, y0, x0]
            b = integrals[i, y1, x1]
            c = integrals[i, y0, x1]
            d = integrals[i, y1, x0]
            hog_cell[i] = (a + b) - (c + d) # 積分画像を計算しているのでこのようなことができる.積分画像にしていない場合はcell毎に要計算
    # ↑積分画像についてはここで終了
    
     
    #// HOG特徴量を計算する
    #// pt: ブロックの中心点
    def get_HOG(self, pt, integrals):
        """ 
        1 ブロックの走査は指定したブロック数毎に行う(例えば2×2) 
        2 histは走査するブロック毎、指定した数の方向によって集計する（例えば9方向）
                    ※1ブロックには指定した数のcellを含んでおり、そのcell毎にエッジの方向が算出されている
        """
        #// ブロックが画像からはみ出していないか確認       
        if pt[1] - R < 0 or \
            pt[0] - R < 0 or \
            pt[1] + R >= integrals[0].shape[1] or \
            pt[0] + R >= integrals[0].shape[0]: return []
     
        # // 与点を中心としたブロックで、
        # // セルごとに勾配ヒストグラムを求めて連結
        hist = np.zeros(N_BIN*BLOCK_SIZE*BLOCK_SIZE) # 1ブロック2×2セル、エッジ方向9だと2*2*9=36次元となる
        tl = [pt[0] - R, 0] # (y,x)のlist。tupleだと値の更新が出来ないためlist
        c = 0
        for i in xrange(BLOCK_SIZE):
            tl[1] = pt[1] - R # xについて
            for j in xrange(BLOCK_SIZE):
                rect = (tl[0], tl[1], CELL_SIZE, CELL_SIZE)
                self.calculate_HOG_InCell(hist[c:c+N_BIN],
                    rect, # 左隅の座標(y,x)、cellのy側サイズ、cellのx側サイズ
                    integrals)
                tl[1] += CELL_SIZE # x側
                c += N_BIN
            tl[0] += CELL_SIZE # y側
        # // L2ノルムで正規化
        hist = cv2.normalize(hist, alpha=1, beta=0, norm_type=cv2.NORM_L2).flatten()
        hist = hist.tolist()
        if [] in hist:
            hist.tolist().remove([])
        return hist # 各ブロック、各方向のhistグラムを返す（getHogの中では特定領域のみ）
    
    def show_HOG(self, image):
        integrals = self.calculate_integral_HOG(image)
        
        im = deepcopy(image)
        im *= 0.5
        first_coordinate = math.ceil(CELL_SIZE*0.5)
        
        # 格子点でHOG計算
        mean_HOG_InBlock = np.zeros(N_BIN,np.float32)
        
        y_block_n = int((im.shape[0] - first_coordinate)/CELL_SIZE)
        x_block_n = int((im.shape[1] - first_coordinate)/CELL_SIZE)
        print y_block_n
        print x_block_n
        y_list = [first_coordinate+CELL_SIZE*i for i in xrange(y_block_n)] 
        x_list = [first_coordinate+CELL_SIZE*i for i in xrange(x_block_n)]
        for y in y_list:
            for x in x_list:
                # (x,y)でのHOGを取得
                hist = self.get_HOG( (y,x), integrals )
                # ブロックが画像からはみ出ていたらcontinue
                if hist == []: continue
                
                # ブロックごとに勾配方向ヒストグラム生成
                mean_HOG_InBlock = np.zeros(N_BIN)
                for i in xrange(N_BIN):
                    for j in xrange(BLOCK_SIZE*BLOCK_SIZE):
                        mean_HOG_InBlock[i] += hist[i+j*N_BIN]
                        
                # L2ノルムで正規化（強い方向が強調される）
                hist = cv2.normalize(mean_HOG_InBlock, alpha=1, beta=0, norm_type=cv2.NORM_L2).flatten()
                
                # 角度ごとに線を描画
                center = np.array([x, y]) # 線分の中心点
                for i in xrange(N_BIN):
                    theta = (i*THETA + 90.0)*math.pi/180.0
                    rd = np.array([CELL_SIZE*0.5*math.cos(theta), CELL_SIZE*0.5*math.sin(theta)])
                    rp = np.int32(center - rd) # int32にしないとよからぬところでマイナス値が出たりする
                    lp = np.int32(center + rd)
                    # 強度によって色を変える
                    color = (mean_HOG_InBlock[i]*255, 255, 255)
                    cv2.line(im, (rp[0],rp[1]), (lp[0],lp[1]), color, 1) # 座標は(x,y)の順に入力すること
        cv2.imshow("Result", im)
        cv2.waitKey()  
        cv2.destroyAllWindows()        

# ここまで
class hogg_adaboost(object):
    def main(self):        
        #pragma comment(lib, "cv.lib")
        #pragma comment(lib, "cxcore.lib")
        #pragma comment(lib, "highgui.lib")
        
        iSampleNum = np.zeros(2)
        # 学習サンプルの読み込みと特徴抽出
        CreateData(samples, iSampleNum);
    
        # //Real AdaBoostによる学習
        Training(samples, iSampleNum);
    
        return
    """    
    def hog(self):
        #include "HOG.h"
        # //勾配強度と勾配方向の算出
        #void CompMagnitudeAndGrad( int x, int y, IplImage *img, double *magnitude, double *grad)
        def CompMagnitudeAndGrad(x, y, img, magnitude, grad):      
            #width = img->width;
            width = self.width
            #height = img->height;
            height = self.height
            #wStep = img->widthStep;
            wStep = self.widthStep
            bpp   = ((img->depth & 255) / 8) * img->nChannels;
            
            unsigned char* imgSource = (unsigned char*) img->imageData;
        
            //横方向の差分
            if(x == 0){
                xgrad = imgSource[y*wStep+(x+0)*bpp] - imgSource[y*wStep+(x+1)*bpp];
            }else if(x == width-1){
                xgrad = imgSource[y*wStep+(x-1)*bpp] - imgSource[y*wStep+(x+0)*bpp];
            }else{
                xgrad = imgSource[y*wStep+(x-1)*bpp] - imgSource[y*wStep+(x+1)*bpp];                        
            }
        
            //縦方向の差分
            if(y == 0){
                ygrad = imgSource[(y+0)*wStep+x*bpp] - imgSource[(y+1)*wStep+x*bpp];
            }else if(y == height-1){
                ygrad = imgSource[(y-1)*wStep+x*bpp] - imgSource[(y+0)*wStep+x*bpp];
            }else{
                ygrad = imgSource[(y-1)*wStep+x*bpp] - imgSource[(y+1)*wStep+x*bpp];
            }
        
            #//勾配強度の算出
            *magnitude = sqrt( xgrad*xgrad + ygrad*ygrad );
        
            #//勾配方向の算出
            *grad = atan2( ygrad, xgrad );
            #//ラジアンから角度へ変換
            *grad  = (*grad * 180) / PI;
            #//符号が負である場合は反転
            if( *grad<0.0){
                *grad += 360.0;
            }
            #//0～360度から0～180度に変換
            if( *grad>180.0){
                *grad -= 180.0;
            }
        
            #//1方向あたりの角度を算出
            angle = 180.0 / ORIENTATION;
            #//勾配方向数で角度を分割
            *grad = *grad / angle;
            
        
    # 勾配方向ヒストグラムの算出
    #void CompHistogram( double cell_hist[], IplImage *img )
    def CompHistogram(self, cell_hist, img):
        {
            int    x, y;
            double grad, magnitude;
        
            //パッチ内の移動
            for(y=0; y<HEIGHT; y++){
                for(x=0; x<WIDTH; x++){
        
                    //勾配強度と勾配方向の算出
                    CompMagnitudeAndGrad( x, y, img, &magnitude, &grad);
        
                    //ヒストグラムに蓄積
                    cell_hist[ (y/CELL)*(WIDTH/CELL)*ORIENTATION + (x/CELL)*ORIENTATION + (int)grad] += magnitude;
                }
            }
        }
    """

    # 特徴量の算出
    #void CompHOG( vector<double> &hog, double cell_hist[] )
    def CompHOG(self, hog, cell_hist):
        {
            int    i,j,k,x,y;
        
            double sum_magnitude;
            double tmp = 0.0;
            double f;
        
            //ブロックの移動
            for(y=0; y<((HEIGHT/CELL)-BLOCK+1); y++){
                for(x=0; x<((WIDTH/CELL)-BLOCK+1); x++){    
        
                    sum_magnitude = 0.0;
                    //セル内の移動
                    for(j=0; j<BLOCK; j++){
                        for(i=0; i<BLOCK; i++){
                            //勾配方向
                            for(k=0; k<ORIENTATION; k++){
                                //正規化のためヒストグラムの総和の二乗を算出
                                tmp = cell_hist[(y+j)*(WIDTH/CELL)*ORIENTATION + (x+i)*ORIENTATION + k];
                                sum_magnitude += tmp * tmp;
                            }
                        }
                    }
        
                    sum_magnitude = 1.0 / sqrt(sum_magnitude + LN_E);
                    
                    //セル内の移動
                    for(j=0; j<BLOCK; j++){
                        for(i=0; i<BLOCK; i++){
                            //勾配方向
                            for(k=0; k<ORIENTATION; k++){
                                //特徴量抽出
                                f = cell_hist[(y+j)*(WIDTH/CELL)*ORIENTATION + (x+i)*ORIENTATION + k] * sum_magnitude;
                                hog.push_back(f);
                            }
                        }
                    }
                }
            }
        }
        
        # HOG特徴量の抽出
        #void HOG( vector<double> &hog, IplImage *img )
    def HOG(hog, img):
        {
            int    i,j,k;
            double *cell_hist;
            cell_hist = new double[ (HEIGHT/CELL) * (WIDTH/CELL) * ORIENTATION];
        
            //0を代入して初期化
            for(j=0; j<(HEIGHT/CELL); j++){
                for(i=0; i<(WIDTH/CELL); i++){
                    for(k=0; k<ORIENTATION; k++){
                        cell_hist[ j*(WIDTH/CELL)*ORIENTATION + i*ORIENTATION + k] = 0.0;
                    }
                }
            }
        
            //勾配方向ヒストグラムの算出
            CompHistogram( cell_hist, img );
        
            //特徴量の算出
            CompHOG( hog, cell_hist );
        
            delete []cell_hist;
        }

    def realadaboost(self):
        POS = 0 
        MEG = 1
        
        # 初期化
        def Initialization(samples, iSampleNum[]): 
            #//学習サンプルの重みを初期化
            for i in xrange(len(samples)):
                if samples[i,0] == POS: # label 
                    samples[i,1] = (1.0 / (iSampleNum[POS] * 2.0)) # weight
                else:
                    samples[i,1] = (1.0 / (iSampleNum[NEG] * 2.0))
            return 
        
        # 確率密度関数の初期化
        def ClearPDF(pdf[][2]):
            pdf = np.zeros((BIN,2))
            return
        
        # //確率密度分布算出
        def CompPDF(samples, dPdf[][2], iFeatureNum):
            # //確率密度関数の初期化
            ClearPDF(dPdf);
        
            for i in xrange(len(samples)):
                dFeature = samples[i].hog[iFeatureNum];
        
                #//[0, 1]の範囲である特徴量をBINの大きさに量子化
                tmp = dFeature * BIN
        
                # //特徴量が[0, 1]の範囲にない場合の処理
                if tmp < 0: tmp = 0
                if tmp >= BIN: tmp = BIN - 1
        
                # //学習サンプルの重みを加算
                dPdf[tmp][samples[i,0]] += samples[i,1]
        
            # //クラス毎の重みの総和を算出
            dSumPos = sum(dPdf[:][POS])
            dSumNeg = sum(dPdf[:][NEG])
        
            # //クラス毎の重みを用いて正規化
            dPdf[:][POS] = dPdf[:][POS] / dSumPos
            dPdf[:][NEG] = dPdf[:][NEG] / dSumNeg
        
            return
        
        
        # //2クラスの確率密度関数のBhattacharya距離を算出
        def EvalPDF(double dPdf[][2]):
            for i in xrange(BIN):
                z= np.sum(np.sqrt(dPdf[:][POS] * dPdf[:][NEG], axis = 1))
            return z
        
        # //弱識別器の選択
        def SelectClassifier(samples, cl, dPdf[][2]):
            dminerror = 1000.0 # 各弱識別器と比較するerrorの初期値
            for i in xrange(len(samples[0].hog):
                # //確率密度関数の作成
                CompPDF(samples, dPdf, i)
                # //弱識別器の評価値を算出
                z = EvalPDF(dPdf)
        
                # //全弱識別器候補の中からエラー最もが低い弱識別器を選択
                if dminerror > z:
                    dminerror = z
                    iFeatureNum = i

            # //エラーが最も低い弱識別器の評価値と弱識別器番号の保存
            #cl->z = dminerror;
            cl_z = dminerror
            #cl->iFeatureNum = iFeatureNum;
            cl_iFeatureNum = iFeatureNum
        
            # //選択された弱識別器を用いて確率密度関数を作成
            CompPDF(samples, dPdf, iFeatureNum)
        
            return
        
        # //弱識別器の出力を算出
        def Prediction(dFeature, dPdf[][2], dEpsilon):        
            # //特徴量を量子化
            tmp = (int)(dFeature * BIN)
            if tmp < 0: tmp = 0
            if tmp >= BIN: tmp = BIN - 1
        
            # //弱識別器の出力を算出
            h = 0.5 * math.log((dPdf[tmp][POS] + dEpsilon)/(dPdf[tmp][NEG] + dEpsilon))
        
            return h
        
        # //学習サンプルの重みを更新
        def UpdateSampleWeight(vector<Sample> &samples, double dPdf[][2], int iFeatureNum, double dEpsilon):
            dSumWeight = 0.0
            for i in xrange(len(samples)):
                # //弱識別器の出力を算出
                dConfidence = Prediction(samples[i].hog[iFeatureNum], dPdf, dEpsilon)
        
                # //弱識別器の出力を用いて学習サンプルの重みを更新
                if samples[i, 0] == POS:
                    samples[i,1] = samples[i,1] * math.exp(-dConfidence)
                else:
                    samples[i,1] = samples[i,1] * math.exp(dConfidence)
        
                # //重みを累積し、重みの総和を算出
                dSumWeight += samples[i,1]
        
            # //サンプルの重みの総和が1となるように正規化
            for i in xrange(len(samples)):
                samples[i,1] = samples[i,1] / dSumWeight
        
            return 
        
        # //確率密度関数の出力
        def WritePDF(double dPdf[][2], int iRound):
            fname =[]
        
            sprintf(fname, "%s%d.txt", DIR_PDF, iRound);
            """
            if((fp = fopen(fname,"w")) == NULL){
                printf("Can Not open PDF file \n");
                exit(1);
            }
            """
        
            for i in xrange(BIN):
                fprintf(fp,"%lf %lf\n", dPdf[i][POS], dPdf[i][NEG])
        
            fclose(fp)
            return 
        
        # //学習データの出力
        def WriteWeakClassifier(cl):
        
            sprintf(fname, "%s", DIR_WEAK_CLASSIFIER);
            """
            if(( fp = fopen(fname,"a")) == NULL){
                printf("Can not open training data file.\n");
                exit(1);
            }
            """
        
            fprintf(fp, "%d %lf\n", cl->iFeatureNum, cl->z);
        
            fclose(fp);
            return
        
        # //識別に必要なパラメータの出力
        def WriteParameter(dEpsilon):
            sprintf(fname, "%s", DIR_WEAK_CLASSIFIER);
            """
            if(( fp = fopen(fname,"w")) == NULL){
                printf("Can not open training data file.\n");
                exit(1);
            }
            """
        
            fprintf(fp, "%lf\n", dEpsilon);
        
            fclose(fp);
        
            return 
        
        # //RealAdaBoostによる識別器の学習
        def Training(samples, iSampleNum):
            # //除算不能を防ぐ係数の算出し、ファイルに出力
            dEpsilon = 1.0 / (iSampleNum[POS] + iSampleNum[NEG])
            WriteParameter(dEpsilon)
        
            cl = new WeakClassifier[MAX_WEAK_CLASSIFIER]
        
            # //学習サンプルの重みを初期化
            Initialization(samples, iSampleNum)
        
            # //学習
            for iRound in xrange(MAX_WEAK_CLASSIFIER):
                printf("Number of weak classifiers : %d\r",iRound + 1)
        
                # //弱識別器候補の中から最もエラーが小さい弱識別器を選択
                SelectClassifier(samples, cl, dPdf)
        
                # //学習サンプルの重みを更新
                UpdateSampleWeight(samples, dPdf, cl_iFeatureNum, dEpsilon)
        
                # //確率密度関数を出力
                WritePDF(dPdf, iRound)
        
                # //学習データ(弱識別器)を出力
                WriteWeakClassifier(cl)
        
            cl_z = None;  cl_iFeatureNum = None
            return 

    def createdata(self):        
        # リストの読み込み
        def SetList(fname[], label):
            if label == POS:
                sprintf(fname, "%s", DIR_POSITIVE_TRAINING_SAMPLE)
            else:
                sprintf(fname, "%s", DIR_NEGATIVE_TRAINING_SAMPLE)
        
            return 
        
        # 学習サンプルの読み込み
        def CreateData(samples, iSampleNum[]):
            IplImage* NormImg = cvCreateImage(cvSize(WIDTH, HEIGHT), IPL_DEPTH_8U, 1);
        
            # ウィンドウの設定
            #cvNamedWindow ("Image", CV_WINDOW_AUTOSIZE);
        
            for i in xrange(2):
                count = 0;
        
                # //サンプルのクラスラベルの設定
                data.label = i;        
        
                # //リストの読み込み
                SetList(fname, i);
                if (fp = fopen(fname, "r")) == None:
                    printf("Can not open a sample list\n%s\n", fname)
                    exit(1)
        
                # //画像の読み込みと特徴量抽出
                while fscanf(fp, "%s", fname) != EOF:
                    printf("image %d\r", samples.size())
        
                    # //グレイスケール画像の読み込み
                    IplImage* img = cvLoadImage(fname, 0);
                    if img == None:
                        printf("Can not open a image\n");
                        return 
        
                    # 正規化画像サイズに拡大縮小
                    cvResize(img, NormImg, CV_INTER_LINEAR)
        
                    # //初期化
                    data.hog.clear();
        
                    # //HOG特徴量の算出
                    HOG(data.hog, NormImg);
                    samples.push_back(data); # 配列の最後にdataを追加
        
                    # //画像の表示
                    cvShowImage("Image", NormImg)
                    cvWaitKey(10)
        
                    cvReleaseImage(img)
                    count++

                iSampleNum[i] = count
                fclose(fp)
        
            cvDestroyWindow ("Image")
            cvReleaseImage(NormImg)
            return 

# mainの場合の挙動        
if __name__ = '__main__':
    imlist = imtools.get_imlist('nail_book03')
    print len(imlist)
    itr = 0
    for imname in imlist:
        if itr ==1: break
        im = cv2.imread(imname, cv.CV_LOAD_IMAGE_GRAYSCALE)
        hog = create_hog_image()
        #hog.main(im)
        hog.show_HOG(im)
        itr += 1
