from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import csv
from django.core.files.storage import default_storage
from django.http import HttpResponse

from .models import Asset
from .serializers import AssetSerializer

from utls.pagination import Pagination


class AssetListCreateView(generics.ListCreateAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    pagination_class = Pagination


class AssetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer


class AssetImportView(APIView):
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        file_path = default_storage.save(file.name, file)

        # 尝试使用 utf-8-sig 编码读取文件
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            assets = []
            for row in reader:
                serializer = AssetSerializer(data=row)
                if serializer.is_valid():
                    assets.append(serializer.save())
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': f'{len(assets)} assets imported successfully'}, status=status.HTTP_201_CREATED)


class AssetExportView(APIView):
    def get(self, request, *args, **kwargs):
        assets = Asset.objects.all()
        serializer = AssetSerializer(assets, many=True)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="assets.csv"'

        writer = csv.writer(response)
        writer.writerow(['asset_id', 'name', 'asset_type', 'created_at', 'owner', 'purchase_date'])  # 添加CSV头部

        for asset in serializer.data:
            writer.writerow(
                [asset['asset_id'], asset['name'], asset['asset_type'], asset['created_at'], asset['owner'],
                 asset['purchase_date']])

        return response
