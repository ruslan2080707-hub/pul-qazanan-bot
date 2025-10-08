# Endpoint to add to main.py for scheduler status

@app.route('/api/admin/scheduler-status', methods=['GET'])
def scheduler_status():
    """
    Проверка статуса планировщика призов
    
    GET /api/admin/scheduler-status?admin_id=5649983054
    """
    try:
        admin_id = request.args.get('admin_id')
        
        # Проверка прав админа
        if int(admin_id) != int(os.getenv('ADMIN_ID')):
            return jsonify({'error': 'Unauthorized'}), 403
        
        if prize_scheduler is None:
            return jsonify({
                'status': 'inactive',
                'message': 'Prize scheduler is not running'
            }), 503
        
        from src.scheduler import get_next_run_times
        next_runs = get_next_run_times(prize_scheduler)
        
        return jsonify({
            'status': 'active',
            'message': 'Prize scheduler is running',
            'next_runs': next_runs,
            'schedule': {
                'daily': 'Every day at 00:05 (Baku time)',
                'weekly': 'Every Monday at 00:10 (Baku time)',
                'monthly': '1st day of month at 00:15 (Baku time)'
            }
        })
            
    except Exception as e:
        logger.error(f"[SCHEDULER] Error getting scheduler status: {e}")
        return jsonify({'error': str(e)}), 500
